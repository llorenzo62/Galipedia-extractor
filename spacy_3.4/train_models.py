from Galutils import *
import spacy
from spacy.tokens import DocBin
from random import shuffle

def pack_labels(sents, nlp, obj_path):
    db = DocBin()
    for sent, tokens in sents:

        spc = nlp(sent)
        if len(spc)!=len(tokens):
            print(f'Warning: {spc} changes tokenization')
            continue

        for sp, token in zip(spc, tokens):
            sp.lemma_=token[2]
            sp.pos_= token[1]

        db.add(spc)
    db.to_disk(obj_path)


def split_samples(labsents, nlp, frac=[0.80, 0.20, 0.0],
                  paths=[]):
    smp=list(labsents)
    shuffle(smp)
    fin = int(len(labsents) * frac[0])
    labeled_sents = smp[:fin]
    pack_labels(labeled_sents, nlp, paths[0])
    fin1 = int(len(labsents) * sum(frac[:2]))
    devel_sents = smp[fin:fin1]
    pack_labels(devel_sents, nlp, paths[1])

    return labeled_sents, devel_sents, smp[fin1:]

base_path=Path.cwd().parent
data_path=base_path/'dataset'
model_path=base_path/'Model'
spacy_path=Path.cwd()
train_path=spacy_path/'Trained'


nlp=spacy.load(model_path/'gl_lg')

labeled_sents=pickle_var(data_path/'labeled_sents_10.pkl')
train_sents,devel_sents,test_sents = split_samples(labeled_sents, nlp,
                                                   paths=[data_path / "train.spacy", data_path / "devel.spacy"])

cfgs=['floret_es','floret_pt', 'base_pt', 'base_es',]#'scratch_es','scratch_pt',]


prefix='bunch10'
script=[]
list_names=[str(item) for item in train_path.glob('*')]
for indx in range(1):

    #base=choice(base_cfg)
    for base in cfgs:
        seed = np.random.randint(1000000)
        name=f'{train_path}/{prefix}_{base}_0'

        i=0

        while name in list_names:
            i+=1
            name = f'{train_path}/{prefix}_{base}_{i}'
        list_names.append(name)
        print('-->',name)
        command=f'python -m spacy train {spacy_path}/{base}.cfg  '
        command+=f'--output {name} --gpu-id=0'
        command+=f' --system.seed={seed}'

        script.append(command)

Path('train_models.sh').write_text('\n'.join(script),encoding='utf8')
