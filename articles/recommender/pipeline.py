from recommender.FeatureManager import FeatureManager
from recommender.feature_extraction.TFIDF import TFIDF
from recommender.feature_extraction.Tokenization import Tokenization
from recommender.model.Ensemble import Ensemble, Mode
from recommender.model.NaiveBayes import NaiveBayes
from recommender.model.SupportVectorMachines import SupportVectorMachines
from recommender.persistence.PickleDS import PickleDS

__author__ = 'Stretchhog'


class Pipeline(object):
	def __init__(self, ds):
		self.feature_manager = FeatureManager()
		self.tfidf = TFIDF(self.feature_manager)
		self.tokenization = Tokenization()
		self.ensemble = Ensemble(Mode.GLOBAL_AVG, [NaiveBayes(), SupportVectorMachines()])
		self.document_cache = []
		self.ds = ds
		self.restore("foo")

	def score(self, document):
		tokens = self.tokenization.tokenize(document)
		features = self.tfidf.single_doc_tfidf(tokens)
		return self.ensemble.score(features)

	def train(self, document, label):
		self.document_cache.append((document, label))
		if len(self.document_cache) >= 2:
			for doc, label in self.document_cache:
				self.update_knowledge(doc, label)
			self.ensemble.train(self.tfidf.get_tfidf(), self.feature_manager.y)
			self.persist()

	def update_knowledge(self, doc, label):
		tokens = self.tokenization.tokenize(doc)
		self.tfidf.update_tfidf(tokens)
		self.feature_manager.add_label(label)

	def persist(self):
		name = "foo"
		data = {
			"name": name,
			"tfidf": {
				"vocabulary": self.tfidf.vocabulary,
				"word_index": self.tfidf.word_index
			},
			"feature_manager": {
				"x": self.feature_manager.features.x,
				"y": self.feature_manager.y
			}
		}
		self.ds.save(name, data)

	def restore(self, name):
		data = self.ds.load(name)
		if data is not None:
			self.feature_manager.features.x = data['feature_manager']['x']
			self.feature_manager.y = data['feature_manager']['y']
			self.tfidf.vocabulary = data['tfidf']['vocabulary']
			self.tfidf.word_index = data['tfidf']['word_index']


text1 = """The remains of 44 victims of the Germanwings plane crash have arrived in Duesseldorf, where they will be returned to families for burial.
Lufthansa sent the coffins by cargo plane on Tuesday night from Marseille.
Elmar Giemulla, a lawyer for some of the families, said the arrival of the remains would give relatives "closure".
Co-pilot Andreas Lubitz is believed to have intentionally flown the Airbus A320 into the French Alps in March, killing 150 people.
Sixteen of the victims were from the Joseph-Koenig-Gymnasium school in Haltern and were returning from an exchange trip in Barcelona when the plane crashed.
Families will be allowed to visit the coffins inside a hangar in Duesseldorf on Wednesday.
Germanwings: The unanswered questions
Who were the victims?
"The families are in denial. They cannot and do not want to realise that their children are dead," Mr Giemulla told AFP.
"It will be brutal when they see the coffins tomorrow, but it is necessary, because they need closure."
The remains of the rest of the victims will be sent back over the coming weeks. The passengers were from 18 countries, including Australia, Argentina and Japan, but most of those on board were either Spanish or German.
The repatriation of some of the bodies was delayed last week because of errors on the death certificates in France."""

text2 = """A woman in Belgium is the first in the world to give birth to a baby using transplanted ovarian tissue frozen when she was still a child, doctors say.
The 27-year-old had an ovary removed at age 13, just before she began invasive treatment for sickle cell anaemia.
Her remaining ovary failed following the treatment, meaning she would have been unlikely to conceive without the transplant.
Experts hope that this procedure could eventually help other young patients.
The woman gave birth to a healthy boy in November 2014, and details of the case were published on Wednesday in the journal Human Reproduction.
Bone marrow transplant
The woman, who has asked to remain anonymous, was diagnosed with sickle cell anaemia at the age of five."""

pipeline = Pipeline(PickleDS())
pipeline.train(text1, False)
pipeline.train(text2, True)

text3 = "woman in belgium is the first in the world to give birth to a baby using transplanted ovarian tissue frozen"
score = pipeline.score(text3)
print(score)
