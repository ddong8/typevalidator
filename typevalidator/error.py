#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/7 21:53
# @File    : error.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from collections import Mapping


class Message(object):
    def __init__(self, text, code, index=None):
        self.text = text
        self.code = code
        self.index = [] if index is None else index

    def __eq__(self, other):
        return isinstance(other, Message) and (
                self.text == other.text
                and self.code == other.code
                and self.index == other.index
        )

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.index:
            return "%s(text=%s, code=%s, index=%s)" % \
                   (class_name, self.text, self.code, self.index)
        return "%s(text=%s, code=%s)" % \
               (class_name, self.text, self.code)


class ValidationError(Mapping, Exception):
    def __init__(self, messages=None, text=None, code=None):
        if messages is None:
            # Instantiated as a ValidationError with a single error message.
            assert text is not None
            assert code is not None
            messages = [Message(text=text, code=code)]
        else:
            # Instantiated as a ValidationError with multiple error messages.
            assert text is None
            assert code is None

        self._messages = messages
        self._message_dict = (
            {}
        )

        # Populate 'self._message_dict'
        for message in messages:
            insert_into = self._message_dict
            for key in message.index[:-1]:
                insert_into = insert_into.setdefault(key, {})  # type: ignore
            insert_key = message.index[-1] if message.index else ""
            insert_into[insert_key] = message.text

    def messages(self, add_prefix=None):
        if add_prefix is not None:
            return [
                Message(
                    text=message.text,
                    code=message.code,
                    index=[add_prefix] + message.index,
                )
                for message in self._messages
            ]
        return list(self._messages)

    def __iter__(self):
        return iter(self._message_dict)

    def __len__(self):
        return len(self._message_dict)

    def __getitem__(self, key):
        return self._message_dict[key]

    def __eq__(self, other):
        return isinstance(other, ValidationError) and self._messages == other._messages

    def __repr__(self):
        class_name = self.__class__.__name__
        if len(self._messages) == 1 and not self._messages[0].index:
            message = self._messages[0]
            return "%s(text=%s, code=%s)" % (class_name, message.text, message.code)
        return "%s(%s)" % (class_name, self._messages)

    def __str__(self):
        if len(self._messages) == 1 and not self._messages[0].index:
            return self._messages[0].text
        return str(dict(self))


class ValidationResult(object):
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def __iter__(self):
        yield self.value
        yield self.error

    def __bool__(self):
        return self.error is None

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.error is not None:
            return "%s(error=%s)" % (class_name, self.error)
        return "%s(value=%s)" % (class_name, self.value)
