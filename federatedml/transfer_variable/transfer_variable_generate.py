#!/usr/bin/env python    
# -*- coding: utf-8 -*- 

#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json
import os
from collections import OrderedDict

BASE_DIR = os.getcwd()
SHEBANG = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
""".strip()
LICENCE = """
#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
""".strip()
TRANSFER_CLASS_TEMPERATE = """
################################################################################
#
# AUTO GENERATED TRANSFER VARIABLE CLASS. DO NOT MODIFY
#
################################################################################

from federatedml.transfer_variable.base_transfer_variable import BaseTransferVariables


# noinspection PyAttributeOutsideInit
class {class_name}(BaseTransferVariables):
    def __init__(self, flowid=0):
        super().__init__(flowid)
        {create_variable}
""".strip()

merge_dict = OrderedDict()  # merged conf in order
init_file_import = OrderedDict() # import class in order


def parse_transfer_variable_conf():
    conf_dir = os.path.join(os.getcwd(), "definition")
    for f_name in sorted(os.listdir(conf_dir)):
        if not f_name.endswith(".json") or f_name == "transfer_conf.json":
            continue

        with open(os.path.join(conf_dir, f_name), "r") as fin:
            var_dict = json.loads(fin.read())
            merge_dict.update(var_dict)
            keys = list(var_dict.keys())
            if len(keys) < 1:
                continue
            if len(keys) > 1:
                raise ValueError("multi class defined in a single json")
            class_name = keys[0]
            file_name = f_name.split(".")[0]
            variable_names = sorted(var_dict.get(class_name).keys())
            init_file_import[file_name] = class_name
        yield file_name, class_name, variable_names


def generate(with_shebang=True, with_licence=True):
    for file_name, class_name, variable_names in parse_transfer_variable_conf():
        class_save_path = os.path.join(os.path.join(BASE_DIR, "transfer_class"), f"{file_name}_transfer_variable.py")
        with open(class_save_path, "w") as f:

            def create_variable(v_name):
                return f"self.{v_name} = self._create_variable(name='{v_name}')"

            temp = TRANSFER_CLASS_TEMPERATE.format(
                class_name=class_name,
                create_variable=f"\n        ".join(map(create_variable, variable_names))
            )
            if with_shebang:
                f.write(SHEBANG)
                f.write("\n")
                f.write("\n")
            if with_licence:
                f.write(LICENCE)
                f.write("\n")
                f.write("\n")
            f.write(temp)
            f.write("\n")
            f.flush()

    # save a merged transfer variable conf, for federation auth checking.
    with open(os.path.join(BASE_DIR, "definition", "transfer_conf.json"), "w") as f:
        json.dump(merge_dict, f, indent=1)

    with open(os.path.join(os.getcwd(), "__init__.py"), "w") as f:
        f.write(SHEBANG)
        f.write("\n")
        f.write("\n")
        f.write(LICENCE)
        f.write("\n")
        f.write("\n")
        for name, class_name in init_file_import.items():
            f.write(f"from .transfer_class.{name}_transfer_variable import {class_name}")
            f.write("\n")


if __name__ == "__main__":
    generate()
