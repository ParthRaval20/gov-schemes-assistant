
import logging, sys, json
logging.basicConfig(level=logging.ERROR)
from rag.agent import translate_scheme_dict, get_llm, warmup
warmup()
d = {
    'scheme_name': 'PM Kisan',
    'description': 'Provides income support to farmers.',
    'benefits': 'Rs 6000 per year',
    'official_link': 'http://pmkisan.gov.in'
}
res = translate_scheme_dict(d, 'hi')
print(json.dumps(res, indent=2, ensure_ascii=False))

