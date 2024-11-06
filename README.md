# `sak`

Swiss Army Knife (sak).

The following env vars need to exist: OPENAI_API_KEY, MEDIUM_API_KEY

**Usage**:

```console
$ sak [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `describe`: Send the blog post specified in FILEPATH...
* `introduce`: Send the blog post specified in FILEPATH...
* `publish`: Publish draft blog posts on Dev.to and...
* `review`: Send the blog post specified in FILEPATH...

## `sak describe`

Send the blog post specified in FILEPATH to ChatGPT to summarise into a one-line description. The result is copied to your clipboard.

**Usage**:

```console
$ sak describe [OPTIONS] FILEPATH
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post being described.  [required]

**Options**:

* `--help`: Show this message and exit.

## `sak introduce`

Send the blog post specified in FILEPATH to ChatGPT to generate an excerpt that can be used as the post's introduction. The chosen excerpt is copied to your clipboard.

**Usage**:

```console
$ sak introduce [OPTIONS] FILEPATH
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post being introduced (generate an excerpt).  [required]

**Options**:

* `--help`: Show this message and exit.

## `sak publish`

Publish draft blog posts on Dev.to and Medium of the specified markdown blog post file.

**Usage**:

```console
$ sak publish [OPTIONS] BLOG_FILEPATH CANONICAL_URL
```

**Arguments**:

* `BLOG_FILEPATH`: The local filepath of the markdown file of the blog post being published.  [required]
* `CANONICAL_URL`: The URL of the original blog post.  [required]

**Options**:

* `--dry-run / --no-dry-run`: If true, then the draft posts will be generated and written to file only. Nothing is posted to dev.to or Medium.  [default: no-dry-run]
* `--only-medium / --no-only-medium`: If true, then only Medium is posted to.  [default: no-only-medium]
* `--only-dev / --no-only-dev`: If true, then only Dev.to is posted to.  [default: no-only-dev]
* `--help`: Show this message and exit.

## `sak review`

Send the blog post specified in FILEPATH to ChatGPT for review.

**Usage**:

```console
$ sak review [OPTIONS] FILEPATH
```

**Arguments**:

* `FILEPATH`: The filepath of the blog post being reviewed.  [required]

**Options**:

* `--help`: Show this message and exit.
