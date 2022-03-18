
from model_handler import CustomHandler


def make_context(ts_path, model_dir='weights/', gpu_id='0'):
    context = type('', (), {})()
    context.system_properties = {'model_dir': f'{model_dir}', 
                                 'gpu_id': gpu_id}
    context.manifest = {'model': {'serializedFile': f'{model_dir}/{ts_path}'}}
    return context

class Demo:
    def __init__(self):
        self.handler = CustomHandler()
        self.handler.initialize(make_context('img_feature.pt'))
        print('handler init')

    def run_model(self, text):
        return self.handler([{'text': text}])[0]


if __name__ == '__main__':
    runner = Demo()

    text = 'зсу'

    result = runner.run_model(text)
    print(result)
