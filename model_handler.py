
import os
import clip
import torch
import logging
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)

class CustomHandler(BaseHandler):
    def __init__(self, ):
        super(CustomHandler, self).__init__()

        self._context = None
        self.initialized = False
        self.model = None
        self.device = torch.device('cpu') #torch.device(f'cuda:{torch.cuda.device_count() - 1}')
        self.dtype = torch.int
        self.use_jit = True
        self.top_k = 5

    def init_models(self, random_img_batch, random_text_batch):
        image_features = self.model.encode_image(random_img_batch)
        text_features = self.model.encode_text(random_text_batch)

    def initialize(self, context):
        model_dir = context.system_properties.get('model_dir')
        serialized_file = context.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)
        img_features_path = os.path.join(model_dir, 'img_feature.pt')
        
        torch.set_grad_enabled(False)
        torch._C._jit_set_bailout_depth(1)
        self.model, _ = clip.load("ViT-B/32", jit=self.use_jit, device=self.device)
        self.model = self.model.eval()
        logger.debug(f'Model loaded from {model_dir}')

        self.img_features = torch.load(img_features_path) 
        
        random_img_batch = torch.rand((1, 3, 224, 224)).to(self.dtype).to(self.device)
        random_text_batch = clip.tokenize(['hi']).to(self.dtype).to(self.device)
        self.init_models(random_img_batch, random_text_batch)
        self.init_models(random_img_batch, random_text_batch)
        self.initialized = True

    def __call__(self, items):
        return self.postprocess(self.inference(self.preprocess(items)))

    def preprocess(self, data):
        items = list()
        for row in data:
            text = row.get('text').decode("utf-8")
            logger.info(f'Text: {text}')
            items.append(
                {
                    'text': text, 
                    'tokenized_text': clip.tokenize(text)
                }
            )
        return items
    
    def inference(self, items, *args, **kwargs):
        with torch.no_grad():
            for item in items:
                text_features = self.model.encode_text(item['tokenized_text'])
                text_features /= text_features.norm(dim=-1, keepdim=True)
                item['text_features'] = text_features
        return items
    
    def get_indices(self, text_features):
        img_similarity = (100.0 * text_features @ self.img_features.T).softmax(dim=-1)
        values, indices = img_similarity.topk(self.top_k)
        return indices.numpy().tolist(), values.numpy().tolist()

    def postprocess(self, items):
        res = list()
        for item in items:
            indices, scores = self.get_indices(item.get('text_features', [''])[0])
            res.append({'indices': indices, 'scores': scores})
        return res