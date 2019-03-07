#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/7 21:49
# @File    : base.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from abc import ABCMeta
from collections import Mapping

from typevalidator.error import ValidationError, ValidationResult
from typevalidator.types import Field, Object


class BaseMetaclass(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        fields = {}

        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                attrs.pop(key)
                fields[key] = value

        # If this class is subclassing other Schema classes, add their fields.
        for base in reversed(bases):
            base_fields = getattr(base, "fields", {})
            for key, value in base_fields.items():
                if isinstance(value, Field) and key not in fields:
                    fields[key] = value

        # using `Field._creation_counter`
        attrs["fields"] = dict(
            sorted(fields.items(), key=lambda item: item[1]._creation_counter)
        )

        return super(BaseMetaclass, mcs).__new__(  # type: ignore
            mcs, name, bases, attrs
        )


class Base(Mapping):
    __metaclass__ = BaseMetaclass
    fields = {}

    def __init__(self, *args, **kwargs):
        if args:
            assert len(args) == 1
            assert not kwargs
            item = args[0]
            if isinstance(item, dict):
                for key in self.fields.keys():
                    if key in item:
                        setattr(self, key, item[key])
            else:
                for key in self.fields.keys():
                    if hasattr(item, key):
                        setattr(self, key, getattr(item, key))
            return

        for key, schema in self.fields.items():
            if key in kwargs:
                value = kwargs.pop(key)
                value, error = schema.validate_or_error(value)
                if error:
                    class_name = self.__class__.__name__
                    error_text = " ".join(
                        [message.text for message in error.messages()]
                    )
                    message = (
                            "Invalid argument %s for %s(). %s" % (key, class_name, error_text)
                    )
                    raise TypeError(message)
                setattr(self, key, value)
            elif schema.has_default():
                setattr(self, key, schema.get_default_value())

        if kwargs:
            key = list(kwargs.keys())[0]
            class_name = self.__class__.__name__
            message = "%s is an invalid keyword argument for %s()." % (key, class_name)
            raise TypeError(message)

    @classmethod
    def validate(cls, data, strict=False):
        required = [key for key, value in cls.fields.items() if not value.has_default()]
        validator = Object(
            properties=cls.fields,
            required=required,
            additional_properties=False if strict else None,
        )
        value = validator.validate(data, strict=strict)
        return cls(value)

    @classmethod
    def validate_or_error(cls, data, strict=False):
        try:
            value = cls.validate(data, strict=strict)
        except ValidationError as error:
            return ValidationResult(value=None, error=error)
        return ValidationResult(value=value, error=None)

    @property
    def is_sparse(self):
        # A schema is sparsely populated if it does not include attributes
        # for all its fields.
        return bool([key for key in self.fields.keys() if not hasattr(self, key)])

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        for key in self.fields.keys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __getitem__(self, key):
        if key not in self.fields or not hasattr(self, key):
            raise KeyError(key)
        field = self.fields[key]
        value = getattr(self, key)
        return field.serialize(value)

    def __iter__(self):
        for key in self.fields:
            if hasattr(self, key):
                yield key

    def __len__(self):
        return len([key for key in self.fields if hasattr(self, key)])

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = {
            key: getattr(self, key) for key in self.fields.keys() if hasattr(self, key)
        }
        argument_str = ", ".join(
            ["%s=%s" % (key, value) for key, value in arguments.items()]
        )
        sparse_indicator = " [sparse]" if self.is_sparse else ""
        return "%s(%s)%s" % (class_name, argument_str, sparse_indicator)

