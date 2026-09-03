# Akay Lab website

The source for [www.theakaylab.com](https://www.theakaylab.com), hosted free on
GitHub Pages. Everything is plain text. Edit a file, commit it, and the site rebuilds
itself in about a minute.

---

## Where to change things

| I want to… | Edit this |
| --- | --- |
| Change any text on a page | the matching `.md` or `.html` file: `index.html`, `science.md`, `join.md`, `contact.md` |
| Add or update a lab member | `_data/people.yml` |
| Add a blog post | a new file in `_posts/` |
| Update the publication list | `_data/publications.yml` |
| Change the navigation, email, address | `_config.yml` |
| Change colours or fonts | the `:root` block at the top of `assets/css/style.css` |
| Change the three research icons | `_includes/science-band.html` |
| Change the organism strip | `_includes/organisms.html` |

You can edit any of these in the browser: open the file on GitHub, click the pencil,
make the change, and press "Commit changes".

---

## Adding a blog post

Create a file in `_posts/` named `YYYY-MM-DD-a-short-slug.md`:

```markdown
---
title: "New paper on snRNA methylation"
date: 2026-09-15 10:00:00 +0100
summary: "One line that shows in the blog list and on the home page."
---

Write the post here in Markdown. **Bold**, *italic*, [links](https://example.com),
and images like this:

![Caption](/assets/img/my-figure.png)
```

The date in the filename controls the ordering, and the five most recent posts appear
on the home page automatically. Put any images in `assets/img/`.

---

## Adding a lab member

Open `_data/people.yml`, copy one of the blocks under `current:`, and change the values:

```yaml
  - name: Dr New Person
    role: Postdoctoral researcher
    photo: new-person.jpg
    bio: |
      A paragraph about them. Markdown works here, so *C. elegans* comes out italic.
```

Save a square photo as `assets/img/people/new-person.jpg` — around 520×520 pixels is
plenty. Leave `photo:` blank and a placeholder initial is shown instead.

When someone leaves, move their name into the `alumni:` list.

---

## Updating the publication list

Three options, in order of least effort:

**From ORCID.** Turn on the Crossref auto-update in your ORCID account settings so new
papers land in your ORCID record by themselves. Then run:

```bash
python3 tools/orcid_to_yaml.py
```

That rewrites `_data/publications.yml` from your public ORCID record. Check the file
and commit it.

**From Google Scholar.** Open your Scholar profile, select the papers, use
Export → BibTeX, save the file as `tools/publications.bib`, then:

```bash
python3 tools/bib_to_yaml.py tools/publications.bib
```

**By hand.** Open `_data/publications.yml` and add an entry in the shape shown in the
comments at the top of that file. Wrap lab members' names in `<strong>` tags to bold
them.

Both scripts need only Python 3, no libraries to install. Neither is magic — check
the output, because ORCID and Scholar records both contain mistakes.

---

## Putting it live

1. Create the repository as **`akaylab.github.io`** under the `akaylab` account or
   organisation, and make it public.
2. Upload everything in this folder to the root of that repository. In GitHub's web
   interface: Add file → Upload files, then drag the contents in. Keep the folder
   structure, including the folders whose names start with an underscore.
3. Go to Settings → Pages. Under "Build and deployment", set Source to
   **Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
4. Wait a minute, then check `https://akaylab.github.io`.

### Pointing theakaylab.com at it

The `CNAME` file in this repo already contains `www.theakaylab.com`. At your domain
registrar, set these DNS records:

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `akaylab.github.io.` |

Check those IP addresses against GitHub's current
[Pages documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
before you trust them — they have been stable for years but they are GitHub's to
change. Delete any old A or CNAME records pointing at your previous host.

DNS can take up to a day to propagate. Once `www.theakaylab.com` loads, go back to
Settings → Pages and tick **Enforce HTTPS**. GitHub issues the certificate for free.

Do not cancel your old hosting until the new site is loading over HTTPS and you have
clicked through every page.

---

## Editing on your own machine (optional)

Not required — GitHub builds the site for you. But if you want a live preview while you
write:

```bash
gem install bundler jekyll
jekyll serve
```

then open `http://localhost:4000`.

---

## Things left to do

- `_data/publications.yml` is empty. Run one of the scripts above.
- Max Brown and Juliet Ibuchim Agu have `Bio to come.` placeholders in
  `_data/people.yml`.
- Juliet Ibuchim Agu has no photo.
- Katarzyna Hencel's bio was written when she was a PhD student and her role is now
  Senior Research Associate — the wording may need updating.
- The blog posts migrated from WordPress were mostly image posts with little text, so
  they are now one-liners. The originals are in your WordPress export if you want to
  restore anything.
- `assets/img/lab-group.jpg` is the 2023 dinner photo, used at the top of the People
  page. Swap it for a newer group photo when you have one.
