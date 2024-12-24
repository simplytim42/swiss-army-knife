# `sak`

Swiss Army Knife (sak).

The following environment variables need to exist:

- OPENAI_API_KEY

- MEDIUM_API_KEY

- DEV_API_KEY

**Usage**:

```console
$ sak [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `version`
* `blog`: Manage blog posts.

## `sak version`

**Usage**:

```console
$ sak version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `sak blog`

Manage blog posts.

**Usage**:

```console
$ sak blog [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `review`: Send a blog post to ChatGPT for review.
* `describe`: Send a blog post to ChatGPT to generate a...
* `title`: Send a blog post to ChatGPT to generate a...
* `introduce`: Send a blog post to ChatGPT to generate an...
* `publish`: Publish a draft blog posts on Dev.to and...

### `sak blog review`

Send a blog post to ChatGPT for review.

**Usage**:

```console
$ sak blog review [OPTIONS] FILEPATH
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post.  [required]

**Options**:

* `--model TEXT`: The model you wish to use.  [default: gpt-4o-mini]
* `--help`: Show this message and exit.

### `sak blog describe`

Send a blog post to ChatGPT to generate a one-line description. The result is copied to your clipboard.

**Usage**:

```console
$ sak blog describe [OPTIONS] FILEPATH
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post.  [required]

**Options**:

* `--model TEXT`: The model you wish to use.  [default: gpt-4o-mini]
* `--help`: Show this message and exit.

### `sak blog title`

Send a blog post to ChatGPT to generate a title. The result is copied to your clipboard.

**Usage**:

```console
$ sak blog title [OPTIONS] FILEPATH
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post.  [required]

**Options**:

* `--model TEXT`: The model you wish to use.  [default: gpt-4o-mini]
* `--help`: Show this message and exit.

### `sak blog introduce`

Send a blog post to ChatGPT to generate an introduction.

**Usage**:

```console
$ sak blog introduce [OPTIONS] FILEPATH
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post.  [required]

**Options**:

* `--model TEXT`: The model you wish to use.  [default: gpt-4o-mini]
* `--help`: Show this message and exit.

### `sak blog publish`

Publish a draft blog posts on Dev.to and Medium.

**Usage**:

```console
$ sak blog publish [OPTIONS] FILEPATH [CANONICAL_URL]
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post.  [required]
* `[CANONICAL_URL]`: The URL of the original blog post.  [default: http://default.com]

**Options**:

* `--dry-run / --no-dry-run`: If true, then the draft posts will be written to file instead.  [default: no-dry-run]
* `--only-medium / --no-only-medium`: If true, send post to Medium only.  [default: no-only-medium]
* `--only-dev / --no-only-dev`: If true, send post to Dev.to only.  [default: no-only-dev]
* `--help`: Show this message and exit.
