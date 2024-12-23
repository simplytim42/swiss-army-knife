from pydantic import BaseModel
from datetime import datetime
import yaml
import emoji
import httpx
import json
import os
import re
import copy
from typing import Optional
from rich import print
from pathlib import Path
from PIL import Image
import cairosvg

class BlogParserError(Exception):
    pass

class FrontMatter(BaseModel):
    draft: bool
    authors: list[str]
    date: datetime
    categories: list[str]
    tags: list[str]
    description: str
    title: str
    main_image: str
    series: Optional[str] = None


class BlogPost(BaseModel):
    content: str
    meta: FrontMatter


class BlogPostParser:
    # map for converting admonitions into a "quote with relevant emoji"
    note_types = {
        "note": ":memo:",
        "abstract": ":notebook:",
        "info": ":information:",
        "tip": ":fire:",
        "success": ":check_mark_button:",
        "question": ":red_question_mark:",
        "warning": ":warning:",
        "failure": ":cross_mark:",
        "danger": ":radioactive:",
        "bug": ":cockroach:",
        "example": ":test_tube:",
        "quote": ":speaking_head:",
    }

    admonition_pattern = re.compile(
        r'[!?]{3} (\w+)(?:\s+"([^"]+)")?\n\n((?:\s{4}.*\n?)+)'
    )
    main_image_pattern = rf'^(.*{re.escape("main-image")}.*)$'
    url_pattern = r"\((https?://[^\s\)]+)\)"
    md_image_pattern = r"!\[(.*?)\]\((https?://[^\s\)]+)\)"
    curly_brace_pattern = r"(!\[.*?\]\(https?://[^\)]+\))\s*\{.*?\}"

    medium_api = "https://api.medium.com/v1"
    dev_api = "https://dev.to/api/articles"

    def __init__(self, blog_post: str):
        self.sak_cache = Path.home() / ".cache" / "sak"
        self.sak_cache.mkdir(parents=True, exist_ok=True)

        self.medium_blog = self._parse_blog(blog_post)
        self.dev_blog = copy.deepcopy(self.medium_blog)
        self.linkedin_blog = copy.deepcopy(self.medium_blog)
        print(self.medium_blog.meta)

    def _replace_headers(self, content: str) -> str:
        # Turn level 2 headers into level 1 and level 3 headers into level 2
        content = content.replace("##", "#")
        return content.replace("###", "##")

    def _format_tag(self, tag: str):
        # remove spaces and hyphens
        return tag.replace("-", " ").title().replace(" ", "")

    def _find_all_images(self, content: str) -> list[str]:
        matches = re.findall(self.md_image_pattern, content)
        return matches

    def _remove_curly_brace_content(self, content: str):
        # This is the extra css that can be passed into material for mkdocs
        return re.sub(self.curly_brace_pattern, r"\1", content, flags=re.MULTILINE)

    def _upload_image_to_medium(
        self, content: str, image_str: str, alt_text: str
    ) -> str:
        # download and convert image
        r = httpx.get(image_str)
        r.raise_for_status()
        og_name = image_str.split("/")[-1]
        image_filename = Path(og_name)

        content_type = r.headers["Content-Type"]
        extension = content_type.split("/")[-1]
        extension = "svg" if extension == "svg+xml" else extension

        with image_filename.open("wb") as f:
            f.write(r.content)

        if extension == "svg":
            png = Path(f"{og_name}.png")
            cairosvg.svg2png(url=image_filename.name, write_to=png.name)
            image_filename.unlink()
            image_filename = png

        image = Image.open(image_filename.name)
        image_filename.unlink()
        image_filename = Path(f"{og_name}.jpeg")
        rgb_image = image.convert("RGB")
        rgb_image.save(image_filename.name, "JPEG")

        # upload to medium
        token = os.getenv("MEDIUM_API_KEY")
        if token is None:
            raise BlogParserError("MEDIUM_API_KEY is not found.")

        with image_filename.open("rb") as image_file:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Accept-Charset": "utf-8",
            }
            files = {"image": (image_filename.name, image_file, "image/jpeg")}
            r = httpx.post(f"{self.medium_api}/images", headers=headers, files=files)
            r.raise_for_status()

        image_filename.unlink()
        image_url = r.json()["data"]["url"]

        lines = content.split("\n")
        for i, line in enumerate(lines):
            if image_str in line:
                lines[i] = f'<img src="{image_url}" alt="{alt_text}">'
        return "\n".join(lines)

    def _get_main_image(self, content: str) -> str:
        # Grabs the post's main image because some sites allow this to be uploaded via metadata
        match = re.search(self.main_image_pattern, content, re.MULTILINE)
        if not match:
            raise BlogParserError("Cannot find Main Image")

        url_match = re.search(self.url_pattern, match.group(1))
        if not url_match:
            raise BlogParserError("Cannot find the URL inside the Main Image line")

        return url_match.group(1)

    def _add_title(self, blog: BlogPost) -> BlogPost:
        # used if the hosting site doesn't want title as metadata. This puts it in the post content.
        title = f"# {blog.meta.title}\n"
        blog.content = title + blog.content
        return blog

    def _note_type_to_emoji(self, note_type: str) -> str:
        # used when converting admonitions. This swaps out the note type for a relevant emoji.
        if note_type not in self.note_types:
            raise BlogParserError(
                f"Note type '{note_type}' does not have a declared Mapping"
            )
        return self.note_types[note_type]

    def _transform_admonitions(self, content):
        # Replace function to transform matched admonition to new format
        def replace_admonition(match):
            note_type = match.group(1)
            title = match.group(2)
            body = match.group(3)

            if title is None:
                title = note_type.title()

            # Indent each line of body and prepend "> "
            note_emoji = self._note_type_to_emoji(note_type)
            indented_body = "".join([f"> {line[4:]}" for line in body.splitlines(True)])

            return f"> {note_emoji} **{title}**\n\n{indented_body}"

        # Apply transformation to the content
        transformed_content = self.admonition_pattern.sub(replace_admonition, content)
        return transformed_content

    def _remove_includes(self, content: str):
        lines = content.split("\n")
        lines = [line for line in lines if "--8<--" not in line]
        return "\n".join(lines)

    def _parse_blog(self, content: str) -> BlogPost:
        front_matter_tmp = ""
        blog_content = ""
        lines = content.splitlines()

        if lines[0] != "---":
            raise BlogParserError("No frontmatter detected!")

        # capture the frontmatter
        end_index = 1
        delimiter = lines[0]
        while end_index < len(lines) and lines[end_index] != delimiter:
            front_matter_tmp += lines[end_index] + "\n"
            end_index += 1

        # skip the closing delimiter
        blog_content = "\n".join(lines[end_index + 1 :]).strip()
        # remove the excerpt marker
        blog_content = blog_content.replace("<!-- more -->\n", "")
        # Apply generic transformations
        blog_content = self._transform_admonitions(blog_content)
        blog_content = self._replace_headers(blog_content)
        blog_content = emoji.emojize(blog_content, language="alias")
        blog_content = self._remove_includes(blog_content)

        # turn frontmatter into a dict and add extra metadata
        front_matter = yaml.safe_load(front_matter_tmp)
        front_matter["tags"] = [self._format_tag(tag) for tag in front_matter["tags"]]
        front_matter["date"] = front_matter["date"]["created"]
        front_matter["main_image"] = self._get_main_image(blog_content)

        return BlogPost(
            content=blog_content.strip(),
            meta=FrontMatter(**front_matter),
        )

    def send_to_medium(self, canonical_url: str, dry_run: bool = False):
        token = os.getenv("MEDIUM_API_KEY")

        if token is None:
            raise BlogParserError("MEDIUM_API_KEY is not found.")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        r = httpx.get(f"{self.medium_api}/me", headers=headers)
        r.raise_for_status()
        data = json.loads(r.text)
        author_id = data["data"]["id"]

        self.medium_blog = self._add_title(self.medium_blog)

        for image in self._find_all_images(self.medium_blog.content):
            alt_text, url = image
            self.medium_blog.content = self._upload_image_to_medium(
                self.medium_blog.content, url, alt_text
            )

        self.medium_blog.content += (
            f"\n\n---\n*Originally published on my [blog]({canonical_url})*"
        )

        payload = {
            "title": self.medium_blog.meta.title,
            "contentFormat": "markdown",
            "content": self.medium_blog.content,
            "canonicalUrl": canonical_url,
            "tags": self.medium_blog.meta.tags,
            "publishStatus": "draft",
        }
        url = f"{self.medium_api}/users/{author_id}/posts"

        if dry_run:
            prefix = "[bold blue][Dry Run Medium][/bold blue]"
            tmp_filepath = self.sak_cache / "Medium.md"
            tmp_filepath.write_text(self.medium_blog.content)
            print(f"{prefix} draft written to {tmp_filepath}")
            print(f"{prefix} URL", url)

            payload_copy = copy.deepcopy(payload)
            payload_copy["content"] = "See cache..."
            print(f"{prefix} Payload:", payload_copy)

            return

        r = httpx.post(
            url=url,
            headers=headers,
            json=payload,
        )
        r.raise_for_status()
        print("Posted to [link=https://medium.com/me/stories/drafts][bold blue]Medium")

    def send_to_dev(self, canonical_url: str, dry_run: bool = False):
        token = os.getenv("DEV_API_KEY")

        if token is None:
            raise BlogParserError("DEV_API_KEY is not found.")

        headers = {
            "api-key": token,
            "Content-Type": "application/json",
        }

        self.dev_blog.content = re.sub(
            r"\s+<figcaption>", "\n<figcaption>", self.dev_blog.content
        )
        self.dev_blog.content = self._remove_curly_brace_content(self.dev_blog.content)

        payload = {
            "article": {
                "title": self.dev_blog.meta.title,
                "published": "false",
                "body_markdown": self.dev_blog.content,
                "tags": self.dev_blog.meta.tags,
                "description": self.dev_blog.meta.description,
                "main_image": self.dev_blog.meta.main_image,
                "canonical_url": canonical_url,
            }
        }
        if self.dev_blog.meta.series:
            payload["article"]["series"] = self.dev_blog.meta.series

        if dry_run:
            prefix = "[bold green][Dry Run Medium][/bold green]"
            tmp_filepath = self.sak_cache / "Dev.to.md"
            tmp_filepath.write_text(self.dev_blog.content)
            print(f"{prefix} draft written to {tmp_filepath}")
            print(f"{prefix} URL", self.dev_api)

            payload_copy = copy.deepcopy(payload)
            payload_copy["article"]["body_markdown"] = "See cache..."
            print(f"{prefix} Payload:", payload_copy)

            return

        r = httpx.post(
            url=self.dev_api,
            headers=headers,
            json=payload,
        )

        r.raise_for_status()
        print("Posted to [link=https://dev.to/dashboard][bold green]Dev.to")


if __name__ == "__main__":
    dry = True
    dir = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir}/../dummy.md") as f:
        parser = BlogPostParser(f.read())
        parser.send_to_medium("https://www.theselftaughtdev.io", dry_run=dry)
        parser.send_to_dev("https://www.theselftaughtdev.io", dry_run=dry)
