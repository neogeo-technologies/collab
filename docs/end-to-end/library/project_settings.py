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

import datetime


def get_variables():
    variables = {
                "RANDOMPROJECTNAME":        "projet - {}".format(datetime.datetime.now()),
                "RANDOMFEATURETYPENAME":    "type - {}".format(datetime.datetime.now()),
                "RANDOMFEATURENAME":        "signalement - {}".format(datetime.datetime.now()),
                "PROJECTEDITION":           " - projet édité",
                "FEATURETYPEEDITION":       " - type édité",
                "FEATUREEDITION":           " - signalement édité",
                }
    return variables
