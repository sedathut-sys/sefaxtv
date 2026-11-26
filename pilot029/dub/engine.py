"""Local CPU EN->TR translation candidates; no inference service."""
import torch
from transformers import MarianMTModel,MarianTokenizer,M2M100ForConditionalGeneration,M2M100Tokenizer
class Translator:
    IDS={"opus":"Helsinki-NLP/opus-mt-tc-big-en-tr","m2m":"facebook/m2m100_418M"}
    def __init__(self,kind):
        self.kind=kind
        ident=self.IDS[kind]
        if kind=="opus":
            self.tokenizer=MarianTokenizer.from_pretrained(ident)
            self.model=MarianMTModel.from_pretrained(ident).eval()
        elif kind=="m2m":
            self.tokenizer=M2M100Tokenizer.from_pretrained(ident,src_lang="en")
            self.model=M2M100ForConditionalGeneration.from_pretrained(ident).eval()
        else:raise ValueError("unknown model")
    @torch.inference_mode()
    def translate(self,text):
        if not text.strip() or len(text)>2000:raise ValueError("invalid input")
        tokens=self.tokenizer(text,return_tensors="pt",truncation=False)
        if tokens["input_ids"].shape[-1]>400:raise ValueError("input too long")
        kw={"max_new_tokens":128,"num_beams":4,"do_sample":False}
        if self.kind=="m2m":kw["forced_bos_token_id"]=self.tokenizer.get_lang_id("tr")
        ids=self.model.generate(**tokens,**kw)
        return self.tokenizer.batch_decode(ids,skip_special_tokens=True)[0].strip()
