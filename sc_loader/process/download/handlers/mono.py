import traceback

from ..url import url_data
from ..civitai import CivitAIModel

def output_result(f):
    def outputter(*args):
        try:
            msg = f(*args)
        except:
            msg = 'ERROR \n' + traceback.format_exc()
            print(msg)
        return msg.replace('\n', '<br>')
    return outputter

@output_result
def generic_handler(civitai_url, update=False):
    model_id, _, version = url_data('generic', civitai_url)
    model = CivitAIModel(model_id, version)
    print(f'Adding {model.type}')
    model.download(update)
    if model.type == 'Package':
        return 'Successfully downloaded package<br>' + model.pkg_results
    return f'Successfully downloaded {model.type}'

@output_result
def generic_updater(civitai_url):
    return generic_handler(civitai_url, True)
