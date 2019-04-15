#!/usr/bin/env python

import io
import json
import uuid

from lib.ConsumeSite import ConsumeSite

MAPA_URL = "https://www.mapa.gob.es/"
GLOBAL_CONSUME_URL = MAPA_URL + "app/consumo-en-hogares/"

CONSUME_URLS = (
                GLOBAL_CONSUME_URL + "consulta04.asp",
                GLOBAL_CONSUME_URL + "consulta05.asp",
                GLOBAL_CONSUME_URL + "consulta06.asp",
                GLOBAL_CONSUME_URL + "consulta10.asp",
                GLOBAL_CONSUME_URL + "consulta11.asp",
               )

generated_files = []
# TODO: Parallelize this for
for site_url in CONSUME_URLS:
    consume_site = ConsumeSite()
    file_name = "data-{0}.json".format(uuid.uuid4().hex)
    generated_files.append(file_name)
    print("Writing {0} data to {1} file".format(site_url, file_name))
    consume_site.get_data(site_url, file_name)

print("List of generated files: {0}". format(generated_files))
