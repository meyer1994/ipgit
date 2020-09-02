# Inter Planetary GIT

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

Because it is possible!

## Table of Contents

- [About](#about)
- [Install](#install)
- [Usage](#usage)
- [Thanks](#thanks)

## About

I think web 3.0 future is promising. I like the idea of a distributed web. As a
consequence, I like IPFS. It is such a cool concept. However, in my opinion,
most people do not use it because it is hard to do so. Go? Running a Docker
container in my machine? What? Can't I just use it as a simple tool or service?

**Yes, you can.**

This is why I created this, extremely simple and limited, web application. It
is just an endpoint. A git remote, for the tech savy. You can configure with
one bash command and just use it. See the (small) example below:

```sh
$ git remote add ipfs http://ipgit.herokuapp.com/
$ git push ipfs
remote: Resolving deltas: 100% (53/53), done.
remote: IPFS hash:
remote: QmU8wwg65D2MpbumSKPTWUhydmAin5jmXbwNhxUWzyeXs1
```

It works the other way around as well. If you want, you can use it to clone git
repositories that are stored in IPFS.

```sh
$ git clone https://ipgit.herokuapp.com/QmZUnAU4Vn7DvDHEnJ1dz2uV2dimf79HNXdffgY9MbQGWP
Cloning into 'QmZUnAU4Vn7DvDHEnJ1dz2uV2dimf79HNXdffgY9MbQGWP'...
$ ls QmZUnAU4Vn7DvDHEnJ1dz2uV2dimf79HNXdffgY9MbQGWP/
Dockerfile  Makefile  app.py  git.py  heroku.yml  post-update  requirements.txt  sender.py
```

That is it! No installation, no requirements. Just plain old git.

Your files will be pinned by default. However, because heroku shuts down the
after some inactivity time, it is not guarantee that your files will be there
when you need them. You should try pinning them into some file pinning service
to avoid loosing it.

## Install

This project uses [fastapi][1] and [uvicorn][2] for server interactions.
[IPFS][3] needs to be running on the local machine for the server to start.
And, obviously, you will need [git][4] installed.

```sh
$ pip install -r requirements.txt
```

## Usage

To run a local version of this project, just execute:

```sh
$ ipfs daemon --init
$ uvicor app:app --reload
$ make local  # optional
```

`make local` adds a `local` remote on `http://localhost:8000` for development.
When developing, you can simply test your modification by calling
`git push local`.

## Thanks

This project would not have been possible without the code in the following
repositories. They helped me understand a lot about git http backend.

- [git_http_backend.py][5]
- [grack][6]


[1]: https://fastapi.tiangolo.com/
[2]: https://uvicorn.org/
[3]: https://ipfs.io/
[4]: https://git-scm.com/

[5]: https://github.com/dvdotsenko/git_http_backend.py
[6]: https://github.com/schacon/grack
