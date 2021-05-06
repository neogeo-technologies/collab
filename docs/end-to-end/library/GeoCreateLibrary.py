# Copyright (c) 2017-2021 Neogeo-Technologies.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import time

import selenium
from selenium.webdriver import ActionChains

from utils import get_driver


def geo_create_project(projectname):
    get_driver().find_element_by_link_text(u"Créer un nouveau projet").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys(projectname)
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[3]/div"
    ).click()
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[3]/div/div[2]/div"
    ).click()
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[4]/div"
    ).click()
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[4]/div/div[2]/div"
    ).click()
    get_driver().find_element_by_xpath("//button[@type='submit']").click()


def geo_create_featuretype(featuretypename):
    get_driver().find_element_by_link_text(
        u"Créer un nouveau type de signalement"
    ).click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys(featuretypename)
    get_driver().find_element_by_xpath("//button[@type='submit']").click()


def geo_create_feature(featuretypename, featurename):
    get_driver().find_element_by_xpath("//div[2]/div/div/div/div/a[2]/i").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys(featurename)
    get_driver().find_element_by_link_text("Dessiner un point").click()
