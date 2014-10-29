#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Test common module of pyramoid_sacrud
"""
import unittest

from pyramid import testing

from pyramid_sacrud.breadcrumbs import breadcrumbs, get_crumb
from pyramid_sacrud.common import (get_obj_from_settings, get_table,
                                   import_from_string, pk_list_to_dict,
                                   update_difference_object)

from .models.auth import User
from .test_views import _TransactionalFixture


class BreadCrumbsTest(unittest.TestCase):

    def test_get_crumb(self):
        crumb = get_crumb('Dashboard', True, 'sa_home', {'name': 'foo'})
        self.assertEqual(crumb, {'visible': True, 'name': 'Dashboard',
                                 'param': {'name': 'foo'},
                                 'view': 'sa_home'})

    def test_breadcrumbs(self):
        bc = breadcrumbs('foo', 'ffoo', 'sa_list')
        self.assertEqual(bc,
                         [{'visible': True, 'name': u'Dashboard',
                           'param': {'name': 'foo'},
                           'view': 'sa_home'},
                          {'visible': True, 'name': 'ffoo',
                           'param': {'name': 'foo'}, 'view': 'sa_list'}])

        bc = breadcrumbs('foo', 'barr', 'sa_create')
        self.assertEqual(bc, [{'visible': True, 'name': 'Dashboard',
                               'param': {'name': 'foo'}, 'view': 'sa_home'},
                              {'visible': True, 'name': 'barr',
                               'param': {'name': 'foo'}, 'view': 'sa_list'},
                              {'visible': False, 'name': 'create',
                               'param': {'name': 'foo'}, 'view': 'sa_list'}])

        bc = breadcrumbs('foo', 'bazz', 'sa_read')
        self.assertEqual(bc, [{'visible': True, 'name': 'Dashboard',
                               'param': {'name': 'foo'}, 'view': 'sa_home'},
                              {'visible': True, 'name': 'bazz',
                               'param': {'name': 'foo'}, 'view': 'sa_list'},
                              {'visible': False, 'name': None,
                               'param': {'name': 'foo'}, 'view': 'sa_list'}])


class CommonTest(_TransactionalFixture):

    def test_get_obj_from_settings(self):
        request = testing.DummyRequest()
        config = testing.setUp(request=request)
        config.registry.settings['foo.User'] =\
            'pyramid_sacrud.tests.models.auth:User'
        obj = get_obj_from_settings(request, 'foo.User')
        self.assertEqual(obj, User)

        config.registry.settings['foo.User'] = User
        obj = get_obj_from_settings(request, 'foo.User')
        self.assertEqual(obj, User)

        config.registry.settings['foo.User'] = 'bad string'
        obj = get_obj_from_settings(request, 'foo.User')
        self.assertEqual(obj, None)

    def test_import_from_string(self):
        self.assertEqual(User,
                         import_from_string('pyramid_sacrud.tests.models.auth:User'))

    def test_update_difference_object(self):
        class Foo: pass
        obj = Foo()
        update_difference_object(obj, "foo", "bar")
        self.assertEqual(obj.foo, "bar")

        obj = {}
        update_difference_object(obj, "foo", "bar")
        self.assertEqual(obj["foo"], "bar")

    def test_pk_list_to_dict(self):
        foo = [1, 2, 3, "a", "b", {"foo": "bar"}]
        resp = pk_list_to_dict(foo)
        self.assertEqual(resp, {1: 2, 3: 'a', 'b': {'foo': 'bar'}})

        foo = [1, 2, 3, "a", "b"]
        resp = pk_list_to_dict(foo)
        self.assertEqual(resp, None)

    def test_get_table(self):
        request = testing.DummyRequest()
        self._init_pyramid_sacrud_settings(request)
        user = get_table('UsEr', request)
        self.assertEqual(user, User)
        foo = get_table('foo', request)
        self.assertEqual(foo, None)
