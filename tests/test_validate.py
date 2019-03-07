#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/7 22:09
# @File    : test_validate.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import typevalidator
from typevalidator import Base


class Artist(Base):
    name = typevalidator.String(max_length=100)


class Album(Base):
    name = typevalidator.String(max_length=100)
    birthday = typevalidator.Date()
    artist = typevalidator.Nested(Artist)


album = Album.validate({
    "name": "Double Negative",
    "birthday": "1995-08-16",
    "artist": {"name": "Jone"}
})

print(album)
# Album(title='Double Negative', release_date=datetime.date(2018, 9, 14), artist=Artist(name='Low'))

print(album.birthday)
# datetime.date(2018, 9, 14)

print(album['birthday'])
# '2018-09-14'

print(dict(album))
# {'title': 'Double Negative', 'release_date': '2018-09-14', 'artist': {'name': 'Low'}}
