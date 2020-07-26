'''
    File name: flask16.05.20.py
    Author: Moshe Blidstein
    Date last modified: 16/05/2020
    Python Version: 3.6
	
'''

from flask import *
import json
import MySQLdb
import pymysql
import random
import pandas as pd
import numpy as np
import regex as re
from natsort import natsorted
from natsort import order_by_index
from natsort import index_natsorted
import requests
from collections import OrderedDict
from collections import Counter
from datetime import datetime
from itertools import chain, groupby, count
from operator import itemgetter
from PIL import Image
# import Image

app = Flask(__name__)
app.debug = True

TITLES = pd.read_csv("/home/moblid/mysite/titlesa.csv", encoding='utf-8')
CRNPD = pd.read_csv("/home/moblid/mysite/crn2.csv")
CRNENGPD = pd.read_csv("/home/moblid/mysite/crneeng.csv")
BOOKPD = pd.read_csv("/home/moblid/mysite/bookreferences2.csv")
BOOKPD["book bibliographic info"] = BOOKPD["book bibliographic info"].astype(str)
BOOKDICT = dict(zip(BOOKPD['book bibliographic info'], BOOKPD['titleref']))
SUBJECT_TAG_TEXT = "<span style='padding-left: 20px; display:block'><br>&nbsp;&nbsp;&nbsp;Tagged with subjects: "
SIM_SUBJECT_TEXT_TAG = "<br><br>    Tagged with subjects:"
BOOK_TAG_TEXT = "<br><br>&nbsp;&nbsp;Found in books: "

YYY = ""


def hyphenate(x):    '''this takes numbers as they are usually printed in indices(e.g., 1-4, 35-7, 109-11) and expands 
					them (e.g., 1, 2, 3, 4, 35, 36, 37, 109, 110, 111). This is probably not very important as it is used 
					in def:crn and def:crneng, both of which are to be replaced'''


result = []
m = str(x)
if re.search('[a-zA-Z]', m):
    result.append(m)
else:
    for part in m.split(','):
        try:
            if '-' in part:
                a, b = part.split('-')
                if len(a) >= len(b):
                    new = a[0:-(len(b))] + b[-(len(b)):]
                    b = new
                    a, b = int(a), int(b)
                else:
                    a, b = int(a), int(b)
                result.extend(range(a, b + 1))
            else:
                try:
                    a = int(part)
                    result.append(a)
                except:
                    continue
        except:
            continue
return result


@app.route('/subjects', methods=['GET', 'POST'])


'''This page lists all the subjects in the database, in two ways: first all of the subjects in 
	a very long list, and then the 200 most used subjects. it also gives the total number of references
	in the database. Not important, nice to have.'''


def one():
    texts_subjects = pd.read_csv("/home/moblid/mysite/texts_subjects2.csv", encoding='utf8')
    texts_subjects["C"] = texts_subjects["C"].apply(hyphenate)
    texts_subjects["number of references in database"] = texts_subjects["C"].str.len()
    texts_subjects = texts_subjects[["subject", "number of references in database"]]
    subjects_count = texts_subjects.sort_values(by=["number of references in database"], ascending=False)
    subjects_count = subjects_count.head(200)
    lsubjects = len(texts_subjects)
    lrest = texts_subjects["number of references in database"].sum()

    return render_template('index2.html', subjects_count=subjects_count.to_html(escape=False), \
                           lsubjects=lsubjects, lrest=lrest, tables=texts_subjects.to_html(escape=False))


@app.route('/biblio', methods=['GET', 'POST'])


'''This page is a list of the books from which I took the indices.'''


def biblio():
    return '''<form method="POST">
</style>
</head>
<title>Mediterranean Index Database</title>
<link rel=stylesheet type=text/css href="{{ url_for("static", filename='/home/moblid/mysite/static/css/style.css') }}">
<div class=page>
<style type="text/css">
  <!--
  .tab { margin-left: 50px; line-height:50px}
  .spacing {margin-bottom:1.5em}
  -->



#blackbox{
position:absolute;
top:0%;
left:0%;
width:100%;
height:100px;
margin-top:0px;
margin-left:0px;
background:lightblue;
}
p{
text-align:center;
font-size:20px;
line-height:10px;
margin:30px;

</style>
</head>
<body>

<div id="blackbox"><p>Tiresias: The Ancient Mediterranean Religions Source Database<br></p></div>


  <br><br><br><br><br>

<br>
<p style="line-height:30px; text-align:left;"
<br>
This page is part of a larger site, <a href="http://tiresias.haifa.ac.il/">Tiresias: The Ancient Mediterranean Religions Source Database</a>


<br><br><br><b>List of book indices included in the database</b><br><br>
The authors of these books are in no way responsible for errors on this database or website. <br><br>
1. Thiessen (2011): Matthew Thiessen, <i> Contesting Conversion: Genealogy, Circumcision, and Identity in Ancient Judaism and Christianity</i>. Oxford: Oxford University Press, 2012<br>
2. Blidstein (2017): Moshe Blidstein, <i> Purity Community and Ritual in Early Christian Literature</i>. Oxford: Oxford University Press, 2017.<br>
3. Matthews (2010): S. Matthews, <i> Perfect Martyr: The Stoning of Stephen and the Construction of Christian Identity</i>. Oxford: Oxford University Press, 2010.<br>
4. Beck (2006): Roger Beck, <i> The Religion of the Mithras Cult in the Roman Empire: Mysteries of the Unconquered Sun</i>. Oxford: Oxford University Press, 2006. <br>
5. Lieu (2015): Judith M. Lieu, <i> Marcion and the Making of a Heretic: God and Scripture in the Second Century</i>. Cambridge: Cambridge University Press, 2015.<br>
6. Vinzent (2013): Markus Vinzent, <i> Christ's Resurrection in Early Christianity and the Making of the New Testament</i>. Ashgate, 2013.<br>
7. Alvar Ezquerra (2008): J. Alvar Ezquerra, <i> Romanising Oriental Gods: Myth, Salvation, and Ethics in the Cults of Cybele, Isis, and Mithras</i>. Leiden: Brill, 2008.<br>
8. Moss (2010): Candida R. Moss, <i> The Other Christs: Imitating Jesus in Ancient Christian Ideologies of Martyrdom</i>. Oxford: Oxford University Press, 2010<br>
9. Peppard (2011): M. Peppard, <i> The Son of God in the Roman World: Divine Sonship in its Social and Political Context</i>. Oxford: Oxford University Press, 2011.<br>
10. Cain (2013): Andrew Cain, <i> Jerome and the Monastic Clergy: A Commentary on Letter 52 to Nepotian</i>. Leiden: Brill, 2013.<br>
11. Collins (2016): John J. Collins, <i> The Apocalyptic Imagination: An Introduction to Jewish Apocalyptic Literature</i>. Eerdmans, 2016<br>
12. Huebner(2013): Sabine R. Huebner, <i> The Family in Roman Egypt: A Comparative Approach to Intergenerational Solidarity and Conflict</i>. Cambridge: Cambridge University Press, 2013<br>
13. Ernst (2009): Allie M. Ernst, <i> Martha from the Margins: The Authority of Martha in Early Christian Tradition</i>. Leiden: Brill, 2009.<br>
14. Alikin (2009): Valeriy A. Alikin, <i> The Earliest History of the Christian Gathering. Origin, Development and Content of the Christian Gathering in the First to Third Centuries</i>. Leiden: Brill, 2009.<br>
15. Seim and Okland (2009): Turid Karlsen Seim and Jorunn Ãkland Seim, eds.,  <i> Metamorphoses: Resurrection, Body and Transformative Practices in Early Christianity</i>. Berlin: De Gruyter, 2009.<br>
16. Boustan, Janssen, Roetzel (2010): Raanan Shaul Boustan, Alex P. Janssen, Calvin J. Roetzel, eds., <i> Violence, Scripture, and Textual Practices in Early Judaism and Christianity</i>. Leiden: Brill, 2010.<br>
17. Nissinen, Uro (2008): Martti Nissinen, Risto Uro, eds., <i> Sacred Marriages: The Divine-Human Sexual Metaphor from Sumer to Early Christianity</i>. Eisenbrauns, 2008.<br>
18. Ramelli (2013): Ilaria Ramelli, <i> The Christian Doctrine of Apokatastasis: A Critical Assessment from the New Testament to Eriugena</i>. Leiden: Brill, 2013.<br>
    19. Perry (2014): Matthew J. Perry, <i> Gender, Manumission, and the Roman Freedwoman</i>. Cambridge: Cambridge University Press, 2014<br>
    20. Nicklas et als. (2010): Tobias Nicklas, Joseph Verheyden, Erik M.M. Eynikel and Florentino Garcia Martinez, eds., <i> Other Worlds and Their Relation to This World: Early Jewish and Ancient Christian Traditions</i>. Leiden: Brill, 2010<br>
    21. Cadwallader (2016): Alan H. Cadwallader, ed., <i> Stones, Bones and the Sacred: Essays on Material Culture and Religion in Honor of Dennis E. Smith</i>. Early Christianity and its literature. SBL Press, 2016<br>
    22. Ando and RÃ¼pke (2006): Clifford Ando and JÃ¶rg RÃ¼pke, eds., <i> Religion and Law in Classical and Christian Rome</i>. Steiner: 2006<br>
    23. Demoen and Praet (2009): Kristoffel Demoen and Danny Praet, eds., <i> Theios Sophistes: Essays on Flavius Philostratus' Vita Apollonii</i>. Leiden: Brill: 2009.<br>
    24. Cohen (2010): <i>The Significance of Yavneh and other Essays in Jewish Hellenism</i>. Tubingen: Mohr Siebeck, 2010<br>
    25. Edmonds (2004): Radcliffe G. Edmonds III, <i> Myths of the Underworld Journey: Plato, Aristophanes, and the âOrphicâ Gold Tablets</i>. Cambridge: Cambridge University Press, 2004<br>
    26. Gruen (2011): Erich S. Gruen, <i> Rethinking the Other in Antiquity</i>. Princeton: Princeton University Press, 2011<br>
    27. Hubbard (2014): Thomas K. Hubbard (ed.), <i> A Companion to Greek and Roman Sexualities</i>. Malden, MA:  Wiley-Blackwell, 2014<br>
    28. Johnston (2008): Sarah I. Johnston, <i> Ancient Greek Divination</i>. Malden, MA:  Wiley-Blackwell, 2008<br>
    29. Lateiner and Spatharas (2016): Donald Lateiner and Dimos Spatharas, eds., <i> The Ancient Emotion of Disgust</i>. Oxford: Oxford University Press, 2016<br>
    30. Gagarin and Cohen (2005): Michael Gagarin and David Cohen, eds., <i> The Cambridge Companion to Ancient Greek Law</i>. Cambridge: Cambridge University Press, 2005<br>
    31. Bickerman and Tropper (2007): E. J. Bickerman and Amram Tropper, <i> Studies in Jewish and Christian History</i>. Leiden: Brill, 2007. <br>
    32. Hirshman (2009): Marc Hirshman, <i> The Stabilization of Rabbinic Culture, 100 C.E.â350 C.E.: Texts on Education and Their Late Antique Context</i>. Oxford: Oxford University Press, 2009 <br>
    33. Nikolsky and Ilan (2014): Ronit Nikolsky and Tal Ilan, <i> Rabbinic Traditions Between Palestine and Babylonia</i>. Leiden: Brill, 2014<br>
    34. Rosen-Zvi (2012): Ishay Rosen-Zvi, <i> The Mishnaic Sotah Ritual: Temple, Gender and Midrash</i>. Leiden: Brill, 2012<br>
    35. Levine (2005): Lee I. Levine, <i> The Ancient Synagogue, The First Thousand Years. 2nd Edition</i>. New Haven: Yale University Press, 2005<br>
    36. Parker (2005): Robert Parker, <i> Polytheism and Society at Athens</i>. Oxford: Oxford University Press, 2005<br>
    37. Versnel (2011): H.S. Versnel, <i> Coping with the Gods: Wayward Readings in Greek Theology</i>. Leiden: Brill, 2011<br>
    38. Pucci (2011): Pietro Pucci, <i> Euripides' Revolution Under Cover: An Essay</i>. Ithaca: Cornell University Press, 2016<br>
    39. Mueller (2002): Hans-Friedrich Mueller, <i> Roman Religion in Valerius Maximus</i>. London and New York: Routledge, 2002<br>
    40. Faraone (1999): Christopher A. Faraone, <i> Ancient Greek Love Magic</i>. Cambridge: Harvard University Press, 1999<br>
    41. Clark (2007): Anna J. Clark, <i> Divine Qualities: Cult and Community in Republican Rome</i>. Oxford: Oxford University Press, 2007<br>
    42. Satlow (2003): Michael L. Satlow, <i> The Gift in Antiquity</i>. Malden, MA; Oxford: Chichester: Wiley-Blackwell, 2013<br>
    43. Petrovic and Petrovic (2016): Andrej Petrovic and Ivana Petrovic, <i> Inner Purity and Pollution in Greek Religion. Volume I: Early Greek Religion</i>. Oxford: Oxford University Press, 2016<br>
    44. Sider (2001): Robert D. Sider (2001), <i> Christian and Pagan in the Roman Empire:  The Witness of Tertullian</i>. Washington D.C: Catholic University of America, 2001<br>
    45. Richlin (2018): Amy Richlin, <i> Slave Theater in the Roman Republic: Plautus and Popular Comedy</i>. Cambridge: Cambridge University Press, 2018<br>
    46. Mikalson (2018): Jon D. Mikalson, <i> New Aspects of Religion in Ancient Athens: Honors, Authorities, Esthetics, and Society</i>. Leiden: Brill, 2016.<br>
    47. Langlands (2018): Rebecca Langlands, <i> Exemplary Ethics in Ancient Rome</i>. Cambridge: Cambridge University Press, 2018<br>
    48. Jamieson (2018): R. B. Jamieson, <i> Jesus' Death and Heavenly Offering in Hebrews</i>. Cambridge: Cambridge University Press, 2018<br>
    49. Singer (2018): P. N. Singer and Philip J. van der Eijk, <i> Galen: Works on Human Nature: Volume 1, Mixtures (De Temperamentis)</i>. Cambridge</i>. Cambridge University Press, 2018<br>
    50. Pandey (2018): Nandini B. Pandey, <i> The Poetics of Power in Augustan Rome</i>. Cambridge: Cambridge University Press, 2018<br>
    51. Keeline (2018): Thomas J. Keeline, <i> The Reception of Cicero in the Early Roman Empire. The Rhetorical Schoolroom and the Creation of a Cultural Legend</i>. Cambridge: Cambridge University Press, 2018<br>
52. Huebner (2018): Sabine R. Huebner, <i> Papyri and the Social World of the New Testament</i>. Cambridge: Cambridge University Press, 2018<br>
53. Bar Asher-Siegal (2018): Michal Bar-Asher Siegal, <i> Jewish-Christian Dialogues on Scripture in Late Antiquity: Heretic Narratives of the Babylonian Talmud</i>. Cambridge: Cambridge University Press, 2018<br>
54. Ruffini (2018): Giovanni R. Ruffini, <i> Life in an Egyptian Village in Late Antiquity: Aphrodito Before and After the Islamic Conquest</i>. Cambridge: Cambridge University Press, 2018<br>
55. Kanarek (2014): Jane L. Kanarek, <i> Biblical narrative and formation rabbinic law</i>. Cambridge: Cambridge University Press, 2014<br>
56. Lorberbaum (2015): Yair Lorberbaum, <i>In God's Image: Myth, Theology, and Law in Classical Judaism</i>. Cambridge: Cambridge University Press, 2015<br>
57. Jassen (2014): Alex P. Jassen, <i> Scripture and Law in the Dead Sea Scrolls</i>. Cambridge: Cambridge University Press, 2014<br>
58. McClellan (2019): Andrew M. McClellan, <i> Abused Bodies in Roman Epic</i>. Cambridge: Cambridge University Press, 2019.<br>
59. Marzano (2018): Annalisa Marzano and Guy P. R. MÃ©traux, eds., <i> The Roman Villa in the Mediterranean Basin Late Republic to Late Antiquity. </i> Cambridge: Cambridge University Press, 2018.<br>
60. Mcglothlin (2018): Thomas D. McGlothlin, <i> Resurrection as Salvation: Development and Conflict in Pre-Nicene Paulinism</i>. Cambridge: Cambridge University Press, 2018.<br>
61. Tabbernee (2007): William Tabbernee, <i> Fake Prophecy and Polluted Sacraments: Ecclesiastical and Imperial Reactions to Montanism</i>. Leiden: Brill, 2007.<br>
62. Horky (2019): Phillip S. Horky, ed., <i> Cosmos in the Ancient World</i>. Cambridge: Cambridge University Press, 2019<br>
63. Hellholm et al. (2010): David Hellholm, Tor Vegge, Ãyvind  Norderval and Christer Hellholm, <i> Ablution, Initiation, and Baptism: Late Antiquity, Early Judaism, and Early Christianity</i>. Berlin: de Gruyter, 2010.<br>
64. Davies (2004): J. P. Davies, <i> Rome's Religious History. Livy, Tacitus and Ammianus on their Gods</i>. Cambridge: Cambridge University Press, 2004.<br>
65. Gwynne (2004): Rosalind W. Gwynne, <i> Logic, Rhetoric and Legal Reasoning in the Qur'an: God's Arguments</i>. London: Routledge, 2009.<br>
67. van den Broek (2013): Roelof van den Broek, <i> Gnostic Religion in Antiquity</i>. Cambridge: Cambridge University Press, 2013.<br>
68. Rupke (2016): JÃ¶rg RÃ¼pke, <i> Religious Deviance in the Roman World Superstition or Individuality? </i> Cambridge: Cambridge University Press, 2016.<br>
69. Ando (2013): Clifford Ando, <i> Imperial Ideology and Provincial Loyalty in the Roman Empire</i>. Berkeley: University of California Press, 2013.<br>
70. Rosenblum (2017): Jordan D. Rosenblum, <i> The Jewish Dietary Laws in the Ancient World</i>. Cambridge: Cambridge University Press, 2017.<br>
71. Brodd and Reed (2011): Jeffrey Brodd and Jonathan L. Reed, <i> Rome and Religion: A Cross-Disciplinary Dialogue on the Imperial Cult</i>. Society of Biblical Literature, 2011.<br>
72. Wynne (2019): J. P. F. Wynne, <i> Cicero on the Philosophy of Religion: On the Nature of the Gods and On Divination</i>. Cambridge: Cambridge University Press, 2019.<br>
73. Rojas (2019): Felipe Rojas, <i> The Remains of the Past and the Invention of Archaeology in Roman Anatolia: Interpreters, Traces, Horizons</i>. Cambridge: Cambridge University Press, 2019.<br>
74. Galinsky (2016): Karl Galinsky, <i> Memory in Ancient Rome and Early Christianity</i>. Oxford: Oxford University Press, 2016.<br>
75. Kowalzig (2007): Barbara Kowalzig, <i> Singing for the Gods: Performances of Myth and Ritual in Archaic and Classical Greece</i>. Oxford: Oxford University Press, 2007.<br>
76. Allison (2018): Dale C. Allison, <i> 4 Baruch. Paraleipomena Jeremiou</i>. Berlin: De Gruyter, 2018.<br>
77. Hillier (1993): Richard Hillier, <i> Arator on the Acts of the Apostles: A Baptismal Commentary</i>. Oxford: Oxford University Press, 1993.<br>
78. Shannon-Henderson (2019). Kelly E. Shannon-Henderson, <i> Religion and Memory in Tacitusâ Annals</i>. Oxford: Oxford University Press, 2019.<br>
79. Cain (2016): Andrew Cain, <i> The Greek Historia Monachorum in Aegypto: Monastic Hagiography in the Late Fourth Century</i>. Oxford: Oxford University Press, 2016.<br>
80. McGowan (1999): Andrew Mcgowan, <i> Ascetic Eucharists: Food and Drink in Early Christian Ritual Meals</i>. Oxford: Oxford University Press, 1999.<br>
81. Hickson (1993): Frances V. Hickson, <i> Roman prayer language: Livy and the Aneid of Vergil</i>. Stuttgart: Teubner, 1993.<br>
82. Simmons (1995): Michael B. Simmons, <i>Arnobius of Sicca: Religious Conflict and Competition in the Age of Diocletian</i>. Oxford: Oxford University Press, 1995.<br>
83. Grypeou and Spurling (2009): Emmanouela Grypeou and Helen Spurling, eds., <i>The Exegetical Encounter between Jews and Christians in Late Antiquity</i>. Leiden: Brill, 2009.<br>
84. Keddie (2019): Anthony Keddie, <i>Class and Power in Roman Palestine: The Socioeconomic Setting of Judaism and Christian Origins</i>. Cambridge: Cambridge University Press, 2019.<br>
85. Marmodoro and Prince (2015): Anna Marmodoro and Brian D. Prince, eds., <i>Causation and Creation in Late Antiquity </i>. Cambridge: Cambridge University Press, 2015.<br>
86. Huffman (2014): Carl A. Huffman, <i> A History of Pythagoreanism.  </i> Cambridge: Cambridge University Press, 2014. <br>
87. KÃ¶nig (2012): Jason KÃ¶nig, <i> Saints and Symposiasts: The Literature of Food and the Symposium in Greco-Roman and Early Christian Culture. </i>. Cambridge: Cambridge University Press, 2012.<br>
88. Sweeney (2013): Mac Sweeney, <i> Foundation Myths and Politics in Ancient Ionia. </i> Cambridge: Cambridge University Press, 2013.<br>
89. Tor (2017): Shaul Tor, <i> Mortal and Divine in Early Greek Epistemology </i>. Cambridge: Cambridge University Press, 2017.<br>
90. Dilley (2019): Paul C. Dilley,  <i> Monasteries and the Care of Souls in Late Antique Christianity: Cognition and Discipline. </i> Cambridge: Cambridge University Press, 2019.<br>
91. Segev (2017): Mor Segev, <i>Aristotle on Religion. </i>. Cambridge: Cambridge University Press, 2017.<br>
92. Hidary (2017): Richard Hidary, <i>Rabbis and Classical Rhetoric: Sophistic Education and Oratory in the Talmud and Midrash</i>. Cambridge: Cambridge University Press, 2017.<br>
93. Hasan Rokem (2003):Galit Hasan-Rokem, <i>Tales of the Neighborhood Jewish Narrative Dialogues in Late Antiquity</i>. Berkeley: University of California Press, 2003.<br>
94. Carr (2004): David M. Carr, Writing on the Tablet of the Heart: Origins of. Scripture and Literature</i>. Oxford: Oxford University Press, 2004.<br>
95. Lidonnici and Lieber (2007): Lynn R. LiDonnici and Andrea Lieber, eds., <i>Heavenly Tablets: Interpretation, Identity and Tradition in Ancient Judaism</i>. Leiden: Brill, 2007.<br>
96. Hayes (2015): Christine Hayes, <i>What's Divine about Divine Law?: Early Perspectives </i>. Princeton: Princeton University Press, 2015. <br>
97. Albrecht (2014):  Felix Albrecht and Reinhard Feldmeier, eds., <i> The Divine Father: Religious and Philosophical Concepts of Divine Parenthood in Antiquity.</i> Leiden: Brill, 2014.<br>
98. Tuori (2016): Kaius Tuori, <i>The Emperor of Law: The Emergence of Roman Imperial Adjudication</i>. Oxford: Oxford University Press, 2016.<br>
99. Piotrkowski (2019): Meron M. Piotrkowski, <i>Priests in Exile: The History of the Temple of Onias and Its Community in the Hellenistic Period</i>. Berlin: De Gruyter, 2019.<br>
100. Dawson (2001): John D. Dawson, <i>Christian Figural Reading and the Fashioning of Identity</i>. Berkeley: University of California Press, 2001.<br>
101. Hanghan (2019): Michael P. Hanghan, <i>Reading Sidonius' Epistles</i>. Cambridge: Cambridge University Press, 2019.<br>
102. Hitch (2017): Sarah Hitch, <i>Animal sacrifice in the ancient Greek world</i>. Cambridge: Cambridge University Press, 2017.<br>
103. Wilson (2012): Walter T. Wilson, <i>The Sentences of Sextus</i>. Atlanta: Society of Biblical Literature, 2012.<br>
104. Griffiths (1975): Griffiths, J. Gwyn. <i>The Isis-Book (Metamorphoses, Book XI). Edited with an Introduction, Translation and Commentary</i>. Leiden: Brill, 1975.<br>
105. Libson (2018): Ayelet H. Libson, <i>Law and self-knowledge in the Talmud. </i> Cambridge: Cambridge University Press, 2018.<br>
106. Brouwer (2013): RenÃ© Brouwer, <i> The Stoic Sage: The Early Stoics on Wisdom, Sagehood and Socrates. </i>Cambridge: Cambridge University Press, 2013.<br>
107. Conybeare (2006): Catherine Conybeare,<i> The Irrational Augustine.</i> Oxford: Oxford University Press, 2006.<br>
108. Burton (2007): Philip Burton, <i> Language in the Confessions of Augustine.</i> Oxford: Oxford University Press, 2007.<br>
109. Cornelli (2013): Gabriele Cornelli, <i> In Search of Pythagoreanism: Pythagoreanism as an Historiographical Category. </i>Berlin: De Gruyter, 2013.<br>
110. Damm (2019): Alex Damm, ed., <i> Religions and Education in Antiquity. Studies in Honor of Michel Desjardins. </i>Leiden: Brill, 2019.<br>
111. Driediger-Murphy and Eidinow (2019): Lindsay G. Driediger-Murphy, Esther Eidinow, eds., <i> Ancient Divination and Experience.</i> Oxford: Oxford University Press, 2019.<br>
112. Frey and Levison (2014): JÃ¶rg Frey and John Levison, in collaboration with: Andrew Bowden, eds. <i> The Holy Spirit, Inspiration, and the Cultures of Antiquity Multidisciplinary Perspectives. </i>De Gruyter, 2014.<br>
113. Kaplan (2015): Jonathan Kaplan, <i> My Perfect One: Typology and Early Rabbinic Interpretation of Song of Songs. </i>Oxford: Oxford University Press, 2015.<br>
114. Monnickendam (2020): Yifat Monnickendam, <i> Jewish Law and Early Christian Identity: Betrothal, Marriage, and Infidelity in the Writings of Ephrem the Syrian.</i> Cambridge: Cambridge University Press, 2020.<br>
115. McDonough (2015): Sean M. McDonough, <i> Christ as Creator: Origins of a New Testament Doctrine.</i> Oxford: Oxford University Press, 2015.<br>
116. Sommerstein and Torrance (2014): Sommerstein, Alan H., and Isabelle C. Torrance. <i> Oaths and Swearing in Ancient Greece.</i> Berlin: De Gruyter, 2014.<br>
117. Thonemann (2020): Peter Thonemann, <i> An Ancient Dream Manual: Artemidorus' the Interpretation of Dreams. </i> Oxford: Oxford University Press, 2020.<br>
118. Fishbane (2003): Michael Fishbane, <i> Biblical Myth and Rabbinic Mythmaking. </i> Oxford: Oxford University Press, 2003.<br>
119. Gaifman (2012): Milette Gaifman,<i> Aniconism in Greek Antiquity.</i> Oxford: Oxford University Press, 2012.<br>
120. Jaffee (2001): Martin S. Jaffee,<i> Torah in the Mouth: Writing and Oral Tradition in Palestinian Judaism 200 BCE - 400 CE. </i>Oxford: Oxford University Press, 2001.<br>
121. Miller and Clay (2019): John F. Miller and Jenny Strauss Clay, eds.,<i> Tracking Hermes, Pursuing Mercury. </i> Oxford: Oxford University Press, 2019.<br>
122. Lunn-Rockliffe (2007): Sophie Lunn-Rockliffe,<i> Ambrosiaster's Political Theology. </i> Oxford: Oxford University Press, 2007.<br>
123. Naiden (2019): Fred S. Naiden,<i> Smoke Signals for the Gods: Ancient Greek Sacrifice from the Archaic through Roman Periods. </i> Oxford: Oxford University Press, 2006.<br>
124. Reif (2006): Stephan C. Reif, <i>Problems with Prayers: Studies in the Textual History of Early Rabbinic Liturgy.</i> Berlin: De Gruyter, 2006.<br>


</p>
    </form>'''


@app.route('/', methods=['GET', 'POST'])


'''the main page of the app'''


def form_example():
    if request.method == 'POST':
        texts_subjects = pd.read_csv("/home/moblid/mysite/texts_subjects1.csv", encoding='utf8')
        YYY = ""
        validated = []
        highly_validated = []
        highly_validated = pd.DataFrame({"a": highly_validated})
        length_highly_validated = 0
        validated = pd.DataFrame({"a": validated})


'''	def:hyph takes a simple string of numbers and hyphenates them, e.g. 1,2,3,4 => 1-4.
'''


def hyph(reflist):
    if "," in reflist:
        try:
            ranges = []
            reflist = reflist.replace(" ", "")
            reflist = [int(k) for k in reflist.split(',')]
            for k, g in groupby(enumerate(reflist), lambda x: x[0] - x[1]):
                group = (map(itemgetter(1), g))
                group = list(map(int, group))
                ranges.append((group[0], group[-1]))
            tt = repr(','.join(['%d' % s if s == e else '%d-%d' % (s, e) for (s, e) in ranges]))
            tt = tt.replace(",", ", ")
            strtt = tt.strip('[]')
            strtt = strtt.replace("'", "")
            return (strtt)
        except:
            reflist = reflist.replace(",", ", ")
            return (reflist)
    else:
        reflist = reflist.replace(",", ", ")
        return (reflist)


def rehyph(refs3):
    refs3 = str(refs3)
    help_list = []
    if "," in refs3:
        if not "." in refs3:
            x = hyph(refs3)
            return (x)
        elif bool(re.search('[a-zA-Z]', refs3)):
            return (refs3)
        else:
            try:
                refs3 = refs3.replace(" ", "")
                listb = refs3.split(",")
                help_df1 = pd.DataFrame({"0": listb})
                help_df1[["0", "1"]] = help_df1["0"].str.rsplit(".", n=1, expand=True)
                help_df1["1"] = help_df1["1"].astype(int)
                help_df1 = help_df1.sort_values(by=["0", "1"])
                help_df1["1"] = help_df1["1"].astype(str)
                help_df2 = help_df1.groupby(["0"])["1"].apply(lambda x: ', '.join(x)).reset_index()
                help_df2 = help_df2.sort_values(by=["0", "1"])
                help_df2["0"] = help_df2["0"].astype(str)
                help_df2["1"] = help_df2["1"].apply(hyph)
                help_df2["1"] = help_df2["1"].str.replace("'", "")
                help_df2["2"] = help_df2["0"] + "." + help_df2["1"]
                help_list = help_df2["2"].values.tolist()
                help_list = [str(i) for i in help_list]
                help_list = [re.sub(",", ", " + str(k.rsplit('.', 1)[0]) + ".", k) for k in help_list]
                help_list = [re.sub("-", "-" + str(k.split('.', 1)[0]) + ".", k) for k in help_list]
                strlonglist = ', '.join(help_list)
                return (strlonglist)
            except:
                return (refs3)
    else:
        return (refs3)


''' def:natural takes a string of references and sorts them using natsorted library. 
	this allows for sorting of complex references such as 2.3, 2.4, 2.15, 11.7 
	where a "usual" sorting as string would render 11.7, 2.15, 2.3, 2.4 (floats also won't work).
'''


def natural(refs1):
    refs1 = str(refs1)
    refs1 = refs1.replace(" ", "")
    listb = refs1.split(",")
    listb = list(set(listb))
    try:
        listb = natsorted(listb)
        listb = ", ".join(listb)
        return (listb)
    except:
        listb = natsorted(listb)
        listb = ", ".join(listb)
        return (listb)


'''def:dup removes duplicates from a list separated by # and sorts them'''


def dup(refs1):


refs1 = str(refs1)
refs1 = refs1.replace("# ", "#")
refs1 = refs1.replace(" # ", "#")
listb = refs1.split("#")
listb = list(set(listb))

try:
    listb = sorted(listb)
    listb = ", ".join(listb)
    return (listb)
except:
    return (listb)


def bookname(bookwithnum):
    try:
        BOOKPD["book bibliographic info"] = BOOKPD["book bibliographic info"].astype(str)
        bookmerge = pd.merge(bookwithnum, BOOKPD, on=["book bibliographic info"], how="left")
        bookmerge = bookmerge[["author", "work", "ref", "subject", "titleref", 'page']]
        bookmerge.columns = [["author", "work", "ref", "subject", "book", 'page']]
        return (bookmerge)
    except:
        return (bookwithnum)


def splitchap(x):
    x = str(x)
    y = x.split('.')[0]
    return y


'''FUNCTIONS NOW USED IN CODE BUT WHICH WILL NOT BE NEEDED IN FUTURE'''


def hyphenate(x):


'''	this takes numbers as they are usually printed in indices(e.g., 1-4, 35-7, 109-11) and expands
	them (e.g., 1, 2, 3, 4, 35, 36, 37, 109, 110, 111). This is probably not very important as it is used 
	in def:crn and def:crneng, both of which are to be replaced'''

result = []
m = str(x)
if re.search('[a-zA-Z]', m):
    result.append(m)
else:
    for part in m.split(','):
        try:
            if '-' in part:
                a, b = part.split('-')
                if len(a) >= len(b):
                    new = a[0:-(len(b))] + b[-(len(b)):]
                    b = new
                    a, b = int(a), int(b)
                else:
                    a, b = int(a), int(b)
                result.extend(range(a, b + 1))
            else:
                try:
                    a = int(part)
                    result.append(a)
                except:
                    continue
        except:
            continue
return result


def hyphenate_b(x):
    '''the same idea like def:hyphenated but for references which may be of a more complicated
     format, e.g., 1.3-5, which should become 1.3, 1.4, 1.5. Again, will not be used once we get rid of crn and crneng'''


rr = []
h = []
m = str(x)
a, b = m.split("-")
try:
    if "." in a:
        a1, a2 = a.split(".")
        b1, b2 = b.split(".")
        a2, b2 = int(a2), int(b2)
        h = list(range(a2, b2 + 1))
        h = [str(i) for i in h]
        rr = [a1 + "." + i for i in h]
        return rr
    else:
        a, b = int(a), int(b)
        h = list(range(a, b + 1))
        h = [str(i) for i in h]
        rr = h
        return rr
except:
    return list(m)

'''this function and the next (crneng) are both for taking a reference, pulling fulltext from api or from 
    a file, and displaying the fulltext. def:crn is for the original language (Greek/Latin/Hebrew/Hebrew) and 
    def:crneng for English translations. both are clearly too copmlicated and have to be written from scratch, 
    so  don't waste time on them.'''


def crn(unciteddata):
    crnmerge = pd.merge(unciteddata, CRNPD, on=["author", "work"], how="left")


if option == "and":
    crnmerge = crnmerge[["author", "work", "ref", "refcite", "subject 1", \
                         "subject 2", "book 1 info", "page 1", "book 2 info", "page 2"]]
else:
    crnmerge = crnmerge[["author", "work", "ref", "refcite", "subject", \
                         'book bibliographic info', 'page']]
crnmerge["ref"] = crnmerge["ref"].astype(str)
crnmerge["refcite"] = crnmerge["refcite"].astype(str)
for a in range(len(crnmerge)):
    refd = str(crnmerge.iloc[a, 3])
    refc = str(crnmerge.iloc[a, 2])
    if refd[1:3] == "ho":
        fltxt = pd.read_csv(refd, encoding='utf8')
        if ("," in refc) or ("-" in refc):
            listrefdd = []
            if "," in refc:
                refc = refc.replace(", ", ",")
                listrefc = refc.split(",")
                for z in range(0, len(listrefc)):
                    if "-" in listrefc[z]:
                        lz = listrefc[z]
                        dop = hyphenate_b(lz)
                        listrefdd.extend(dop)
                    else:
                        listrefdd.append(listrefc[z])
            elif "," not in refc:
                if "-" in refc:
                    listrefdd = hyphenate_b(refc)
            if "annal" in refd:
                listrefee = []
                for x in range(0, len(listrefdd)):
                    opp = listrefdd[x]
                    if opp.count(".") == 2:
                        cut = str(opp.split('.', 2)[0]) + str(opp.split('.', 2)[1])
                        listrefee.append(cut)
                    else:
                        listrefee.append(opp)
                listrefdd = listrefee
            fltxt['ref'] = fltxt['ref'].astype(str)
            listreftext = []
            listrefdd_df = pd.DataFrame({"a": listrefdd})
            fltxta = fltxt.loc[fltxt['ref'].isin(listrefdd_df["a"])]
            fltxta["results"] = fltxta["ref"] + ". " + fltxta["text"]
            listreftext = fltxta['results'].values.tolist()
            listreftext = natsorted(listreftext)
            if len(listreftext) == 0:
                strreflink = listrefdd
            else:
                strreflink = " ".join(listreftext)
                strreflink = strreflink.replace("\r\n", "<br>")
                strreflink = strreflink.replace("\\r\\n", "<br>")
            crnmerge.iloc[a, 3] = strreflink
        else:
            refg = refc
            if "annal" in refd:
                refg = refg.split('.', 2)[0] + "." + refg.split('.', 2)[1]
            fltxt['ref'] = fltxt['ref'].astype(str)
            listreftext = []
            fltxta = fltxt.loc[fltxt['ref'] == refg]
            fltxta["results"] = fltxta["ref"] + ". " + fltxta["text"]
            listreftext = fltxta['results'].values.tolist()
            if len(listreftext) == 0:
                strreflink = str(refg)
            else:
                strreflink = " ".join(listreftext)
            crnmerge.iloc[a, 3] = strreflink
    elif refd[0:2] == "ht":
        if ("," in refc):
            if "tlg0059" in refd:
                refc = refc.replace("[a-z]", "")
            refc = refc.replace(", ", ",")
            refc = refc.replace(", ", ",")
            listrefc = refc.split(",")
            listreftext = []
            for x in range(0, len(listrefc)):
                try:
                    refe = refd.replace("linkref", listrefc[x])
                    res = requests.get(refe)
                    if "sefaria" in refd:
                        res.encoding = 'unicode-escape'
                    else:
                        res.encoding = 'utf-8'
                    res2 = res.text
                    if "went wrong" in res2:
                        res2 = "full text unavailable"
                    if "sefaria" in refd:
                        res2 = res2.split('"he":', 1)[1]
                        # res2 = res2.split('"]',1)[0]
                        res2 = res2.split(', "he', 1)[0]
                        res2 = res2.split(', "is', 1)[0]
                        res2 = res2.split(', "version', 1)[0]
                    if len(res2) > 2000:
                        res2 = res2[0:2000]
                    res2 = res2.replace("^', '", "")
                    res2 = res2.replace("\n\n\n", "\n")
                    res2 = res2.replace("\n\n", "\n")
                    res2 = res2.replace("\n", " ")
                    res2 = res2.replace("\t", "")
                    listreftext.append(listrefc[x] + ".")
                    listreftext.append(res2)
                    listreftext.append("<br/>")
                except:
                    listreftext.append("empty")
            strreflink = str(listreftext)
            strreflink = str(listreftext)
            strreflink = strreflink[2:-2]
            strreflink = strreflink.replace("', '", "")
            crnmerge.iloc[a, 3] = strreflink
        else:
            try:
                if "tlg0059" in refd:
                    refc = re.sub(r'[a-z]-[a-z]', '', refc)
                    refc = refc.replace("[a-z]", "")
                if "stoa0275" in refd:
                    refc = refc.split('.', 1)[0]
                refd = refd.replace("linkref", refc)
                res = requests.get(refd)
                if "sefaria" in refd:
                    res.encoding = 'unicode-escape'
                else:
                    res.encoding = 'utf-8'
                res2 = res.text
                if "went wrong" in res2:
                    res2 = "full text unavailable"
                if "sefaria" in refd:
                    res2 = res2.split('"he":', 1)[1]
                    res2 = res2.split(', "he', 1)[0]
                    res2 = res2.split(', "is', 1)[0]
                    res2 = res2.split(', "version', 1)[0]
                if len(res2) > 2000:
                    res2 = res2[0:2000]
                res2 = res2.replace("\n\n\n", "\n")
                res2 = res2.replace("\n\n", "\n")
                res2 = res2.replace("\n", " ")
                res2 = res2.replace("\t", "")
                crnmerge.iloc[a, 3] = res2
            except:
                crnmerge.iloc[a, 3] = refd
    else:
        crnmerge.iloc[a, 3] = refd
citeddata = crnmerge
return (citeddata)


def crneng(unciteddata):
    unciteddata["author"] = unciteddata["author"].str.lower()
    unciteddata["work"] = unciteddata["work"].str.lower()
    CRNENGPD["author"] = CRNENGPD["author"].str.lower()
    CRNENGPD["work"] = CRNENGPD["work"].str.lower()
    crnengmerge = pd.merge(unciteddata, CRNENGPD, on=["author", "work"], how="left")
    if option == "and":
        crnengmerge = crnengmerge[["author", "work", "ref", "refcite", "refengcite", "subject 1", "subject 2" \
            , "book 1 info", "page 1", "book 2 info", "page 2"]]
    else:
        crnengmerge = crnengmerge[["author", "work", "ref", "refcite", "refengcite", \
                                   "subject", 'book bibliographic info', 'page']]
    crnengmerge["ref"] = crnengmerge["ref"].astype(str)
    crnengmerge["refengcite"] = crnengmerge["refengcite"].astype(str)
    for a in range(len(crnengmerge.index)):
        refd = str(crnengmerge.iloc[a, 4])
        refc = str(crnengmerge.iloc[a, 2])
        if refd[0:2] == "ht":
            if "," in refc:
                refc = refc.replace(" ", "")
                listrefc = refc.split(",")
                listreftext = []
                for x in range(0, len(listrefc)):
                    try:
                        if "tlg0059" in refd:
                            if listrefc[x][-1] == "a" or listrefc[x][-1] == "b" or \
                                    listrefc[x][-1] == "c" or listrefc[x][-1] == "d" or listrefc[x][-1] == "e":
                                listrefc[x] = listrefc[x][:-1]
                        refe = refd.replace("linkref", listrefc[x])
                        res = requests.get(refe)
                        res.encoding = 'utf-8'
                        if "sefaria" in refd:
                            res.encoding = 'unicode-escape'
                        res2 = res.text
                        if len(res2) > 3000:
                            res2 = res2[0:3000]
                        if "went wrong" in res2:
                            res2 = "text not available"
                        if "sefaria" in refd:
                            res2 = res2.split('"text":', 1)[1]
                            res2 = res2.split(', "next"', 1)[0]
                            res2 = res2.split(', "he"', 1)[0]
                            res2 = res2.split(', "heT', 1)[0]
                            res2 = res2.split(', "heV', 1)[0]
                            res2 = res2.split(', "titleV', 1)[0]
                            res2 = res2.split(', "is[A-Z]', 1)[0]
                            res2 = res2.split(', "isD', 1)[0]
                            res2 = res2.split(', "isC', 1)[0]
                            res2 = res2.split(', "versi', 1)[0]
                            res2 = res2.split('sectionR', 1)[0]
                            res2 = res2.split('ref', 1)[0]
                            res2 = res2.replace("\[\"", "")
                            res2 = res2.replace("\"\]", "")
                            res2 = res2.replace("\", \"", " ")
                            res2 = res2.replace("\",\"", " ")
                            res2 = res2.replace("$[\"", "")
                            res2 = res2.replace("\"]^", "")
                        res2 = res2.replace("\n\n\n", "\n")
                        res2 = res2.replace("\n\n", "\n")
                        res2 = res2.replace("\n", " ")
                        res2 = res2.replace("\t", "")
                        listreftext.append(listrefc[x] + ".")
                        listreftext.append(res2)
                        listreftext.append("<br/>")
                    except:
                        listreftext.append("empty")
                listreftext = natsorted(listreftext)
                strreflink = str(listreftext)
                strreflink = strreflink[2:-2]
                strreflink = strreflink.replace("', '", "")
                crnengmerge.iloc[a, 4] = strreflink
            else:
                try:
                    if "tlg0059" in refd:
                        refc = refc.replace("[a-z]", "")
                    refd = refd.replace("linkref", refc)
                    res = requests.get(refd)
                    res.encoding = 'utf-8'
                    if "sefaria" in refd:
                        res.encoding = 'unicode-escape'
                    res2 = res.text
                    if "sefaria" in refd:
                        res2 = res2.split('"text":', 1)[1]
                        res2 = res2.split(', "next"', 1)[0]
                        res2 = res2.split(', "he"', 1)[0]
                        res2 = res2.split(', "heT', 1)[0]
                        res2 = res2.split(', "heV', 1)[0]
                        res2 = res2.split(', "heE', 1)[0]
                        res2 = res2.split(', "titleV', 1)[0]
                        res2 = res2.split(', "isC', 1)[0]
                        res2 = res2.split(', "isD', 1)[0]
                        res2 = res2.split(', "vers', 1)[0]
                        res2 = res2.replace("\[\"", "")
                        res2 = res2.replace("\"\]", "")
                        res2 = res2.replace("\", \"", " ")
                        res2 = res2.replace("\",\"", " ")
                    if "went wrong" in res2:
                        res2 = "English translation unavailable"
                    res2 = res2.replace("\n", " ")
                    res2 = res2.replace("\t", "")
                    crnengmerge.iloc[a, 4] = res2
                except:
                    crnengmerge.iloc[a, 4] = refd
        elif refd[0:2] == "xx":
            refd = refd.replace("xx", "")
            fltxt = pd.read_csv(refd, encoding='utf8')
            refc = refc.replace("\. ", ".")
            if ("," in refc) or ("-" in refc):
                listrefdd = []
                if "," in refc:
                    refc = refc.replace(", ", ",")
                    listrefc = refc.split(",")
                    for z in range(0, len(listrefc)):
                        if "-" in listrefc[z]:
                            lz = listrefc[z]
                            dop = hyphenate_b(lz)
                            listrefdd.extend(dop)
                        else:
                            listrefdd.append(listrefc[z])
                elif "," not in refc:
                    if "-" in refc:
                        listrefdd = hyphenate_b(refc)
                if "annal" in refd:
                    listrefee = []
                    for x in range(0, len(listrefdd)):
                        opp = listrefdd[x]
                        if opp.count(".") == 2:
                            cut = str(opp.split('.', 2)[0]) + str(opp.split('.', 2)[1])
                            listrefee.append(cut)
                        else:
                            listrefee.append(opp)
                    listrefdd = listrefee
                fltxt['ref'] = fltxt['ref'].astype(str)
                listreftext = []
                listrefdd_df = pd.DataFrame({"a": listrefdd})
                fltxta = fltxt.loc[fltxt['ref'].isin(listrefdd_df["a"])]
                fltxta["results"] = fltxta["ref"] + ". " + fltxta["text"]
                listreftext = fltxta['results'].values.tolist()
                if len(listreftext) == 0:
                    strreflink = listrefdd
                else:
                    strreflink = " ".join(listreftext)
                    strreflink = strreflink.replace("\r\n", "<br>")
                    strreflink = strreflink.replace("\\r\\n", "<br>")
                crnengmerge.iloc[a, 4] = strreflink
            else:
                refg = refc
                fltxt['ref'] = fltxt['ref'].astype(str)
                listreftext = []
                fltxta = fltxt.loc[fltxt['ref'] == refg]
                fltxta["results"] = fltxta["ref"] + ". " + fltxta["text"]
                listreftext = fltxta['results'].values.tolist()
                if len(listreftext) == 0:
                    strreflink = str(refg)
                else:
                    strreflink = " ".join(listreftext)
                    strreflink = strreflink.replace("\n", "")
                crnengmerge.iloc[a, 4] = strreflink
        else:
            crnengmerge.iloc[a, 4] = "ooo"
    crnengmerge["author"] = crnengmerge["author"].str.title()
    crnengmerge["work"] = crnengmerge["work"].str.title()
    crnengmerge["author"] = crnengmerge["author"].str.replace("Of", "of")
    citeddata = crnengmerge
    return (citeddata)


if "step" not in request.form:
    empty = ""
    c = request.form.get('c')
    d = request.form.get('d')
    option = request.form.get('option')
    email = request.form.get('email')
    now = str(datetime.now())
    searchford = []
    length_validated = 0
    d_texts_subjects = 1
    d_subjects = []

    fd = open("/home/moblid/mysite/emails.csv", "a")
    fd.write(email)
    fd.write(",".join([now, c, d]))
    fd.write("\n")
    fd.close()
    pd.set_option('display.max_colwidth', -1)

    if c == "":
        randrow = random.randint(0, 2000)
        texts_subjects["number of references in database"] = texts_subjects["C"].str.len()
        texts_subjects = texts_subjects[["subject", "number of references in database"]]
        subjects_count = texts_subjects.sort_values(by= \
                                                        ["number of references in database"], ascending=False)
        subjects_count = subjects_count.head(2000)
        c = subjects_count.iloc[randrow, 0]
    db = MySQLdb.connect(
        host='moblid.mysql.pythonanywhere-services.com',
        user='moblid',
        passwd='s4MYP9KSyYkZ6B6',
        db='moblid$default',
        charset='utf8')
    dds = []
    if c:
        c2 = "'%" + c + "%'"
        sql_for_df_sub = "SELECT * FROM texts_subjects WHERE subject like " + c2
        texts_subjects1 = pd.read_sql_query(sql_for_df_sub, db)
        subjects = texts_subjects1['subject'].values.tolist()
        texts_subjects1["C"] = texts_subjects1["C"].apply(hyphenate)
        cs = texts_subjects1['C'].values.tolist()
        ccs = [item for sublist in cs for item in sublist]
        lccs = len(ccs)
        pd.set_option('display.max_colwidth', -1)
        if option == "and":
            d2 = "'%" + d + "%'"
            sql_for_df_sub_d = "SELECT * FROM texts_subjects WHERE subject like " + d2
            d_texts_subjects = pd.read_sql_query(sql_for_df_sub_d, db)
            d_subjects = d_texts_subjects['subject'].values.tolist()
            d_texts_subjects["C"] = d_texts_subjects["C"].apply(hyphenate)
            ds = d_texts_subjects['C'].values.tolist()
            dds = [item for sublist in ds for item in sublist]

    return render_template('index.html', subjects=subjects \
                           , step="choose_lower", c=c, lccs=lccs, ccs=ccs, dds=dds, \
                           d=d, option=option, d_texts_subjects=d_texts_subjects, \
                           d_subjects=d_subjects)


elif request.form["step"] == "choose_upper":
    TITLES = pd.read_csv("/home/moblid/mysite/titlesa.csv", encoding='utf-8')
    empty = ""
    c_subject = request.form.get('c')
    ccs = request.form.getlist('ccs')
    dds = request.form.getlist('dds')
    k = request.form.getlist('chkbox')
    kd = request.form.getlist('d_chkbox')
    fulltext = request.form.get('fulltext')
    author = request.form.get('author')
    add_key = request.form.get('add_key')
    no_key = request.form.get('no_key')
    work = request.form.get('work')
    ref = request.form.get('ref')
    lang = request.form.get('language')
    cs = request.form.get('centstart')
    ce = request.form.get('centend')
    option = request.form.get('option')
    length_validated = 0
    l = len(k)

    if fulltext != "f":
        full = "fulltext"
    else:
        full = "not full"
    fd = open("/home/moblid/mysite/emails.csv", "a")
    fd.write(",".join([full, author, work, ref, lang, cs, ce, option, str(len(ccs))]))
    fd.write("\n")
    fd.close()
    pd.set_option('display.max_colwidth', -1)
    df = []
    df = pd.DataFrame({"a": df})
    df1 = []
    df1 = pd.DataFrame({"subject": df1, "ref": df1, "page": df1, \
                        "book bibliographic info": df1, "number": df1, "C": df1})
    ccs = ",".join(ccs)
    ccs = ccs.replace("[", "")
    ccs = ccs.replace("]", "")
    ccs = ccs.split(", ")
    ccs1 = tuple(ccs)
    db = MySQLdb.connect(
        host='moblid.mysql.pythonanywhere-services.com',
        user='moblid',
        passwd='s4MYP9KSyYkZ6B6',
        db='moblid$default',
        charset='utf8')
    sql_for_df = "SELECT * FROM textsa WHERE C IN {}".format(ccs1)
    c2 = "'%" + c_subject + "%'"
    textsa = pd.read_sql_query(sql_for_df, db)
    if add_key:
        textsa = textsa[textsa['subject'].str.contains(add_key)]
    if no_key:
        textsa = textsa[~textsa['subject'].str.contains(no_key)]
    textsa = textsa[textsa['subject'].isin(k)]
    textsa['number'] = textsa['number'].astype(str)
    textsa['number'] = textsa['number'].str.replace('\\.0', '')
    TITLES['number'] = TITLES['number'].astype(str)
    TITLES['number'] = TITLES['number'].str.replace('\\.0', '')
    TITLES["title1"] = TITLES["title1"].str.title()
    TITLES["author1"] = TITLES["author1"].str.title()
    textsb = pd.merge(textsa, TITLES, on="number", how="left")
    textsb.rename(columns={"title1": "work"}, inplace=True)
    textsb.rename(columns={"author1": "author"}, inplace=True)
    data = textsb[["author", "book bibliographic info", "centend" \
        , "centstart", "language", "page", "ref", "subject", "work"]]
    data["ref"] = data["ref"].str.replace("DK", "")
    data["ref"] = data["ref"].str.replace("Fr\.", "")
    data["ref"] = data["ref"].str.lower()
    data["ref"] = data["ref"].str.strip()
    if len(data.index) != 0:
        data = data[~data.applymap(lambda x: len(str(x)) > 90).any(axis=1)]
    else:
        empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"
    length_data = len(data.ref)

    data['book bibliographic info'] = data['book bibliographic info'].astype(str)
    bb = data.loc[:, "subject"]
    bb1 = bb.drop_duplicates(keep="first")
    Listkk = bb1.tolist()
    length_data = len(data.ref)
    if cs != "any":
        cs = int(cs)
        data = data.loc[data['centend'] != "Nan"]
        data[['centend']] = data[['centend']].apply(pd.to_numeric)
        data = data[data.centend >= cs]
    if ce != "any":
        ce = int(ce)
        data = data.loc[data['centstart'] != "Nan"]
        data[['centstart']] = data[['centstart']].apply(pd.to_numeric)
        data = data[data.centstart <= ce]
    if lang != "all":
        data = data[data["language"].str.contains(lang, na=False)]
    if author:
        data = data[data["author"].str.contains(author, na=False)]
    if work:
        data = data[data["work"].str.contains(work, na=False)]
    if ref:
        if "." in ref:
            data = data[data.ref == ref]
        if "." not in ref:
            data["refchap"] = data["ref"].apply(splitchap)
            data = data[data.refchap == ref]
    if option == "and":
        dfd = []
        dfd = pd.DataFrame({"a": dfd})
        dfd1 = []
        dfd1 = pd.DataFrame({"subject": dfd1, "ref": dfd1, "page": dfd1, \
                             "book bibliographic info": dfd1, "number": dfd1, "C": dfd1})
        dds = ",".join(dds)
        dds = dds.replace("[", "")
        dds = dds.replace("]", "")
        dds = dds.split(", ")
        dds1 = tuple(dds)
        db = MySQLdb.connect(
            host='moblid.mysql.pythonanywhere-services.com',
            user='moblid',
            passwd='s4MYP9KSyYkZ6B6',
            db='moblid$default',
            charset='utf8')
        sql_for_dfd = "SELECT * FROM textsa WHERE C IN {}".format(dds1)
        textsad = pd.read_sql_query(sql_for_dfd, db)
        data1 = data
        textsa = textsad[["book bibliographic info", "page", "ref", "subject", "number"]]
        textsa['number'] = textsa['number'].astype(str)
        textsa['number'] = textsa['number'].str.replace('\\.0', '')
        textsa['ref'] = textsa['ref'].str.replace('\. ', '.')
        TITLES['number'] = TITLES['number'].astype(str)
        TITLES['number'] = TITLES['number'].str.replace('\\.0', '')
        textsb = pd.merge(textsa, TITLES, on="number", how="left")
        textsb.rename(columns={"title1": "work"}, inplace=True)
        textsb.rename(columns={"author1": "author"}, inplace=True)
        data2 = textsb[["author", "book bibliographic info", "centend", \
                        "centstart", "language", "page", "ref", "subject", "work"]]
        data1["ref"] = data1["ref"].astype(str)
        data2["ref"] = data2["ref"].astype(str)
        data1["results"] = data1["work"].map(str) + " " + data1["ref"]
        data2["results"] = data2["work"].map(str) + " " + data2["ref"]
        data = data1.merge(data2, on="results", how="inner")
        bb3 = data.loc[:, "subject_y"]
        bb4 = bb3.drop_duplicates(keep="first")
        Listbb3 = bb4.tolist()
        data['page_y'] = data['page_y'].astype(str)
        data['page_x'] = data['page_x'].astype(str)
        data = data.drop(["ref_y", "work_y", "author_y", "results"], axis=1)
        data['ref_x'] = data['ref_x'].astype(str)
        bb = data.loc[:, "subject_x"]
        bb1 = bb.drop_duplicates(keep="first")
        Listkk = bb1.tolist()
        data.rename(columns={"author_x": "author"}, inplace=True)
        data.rename(columns={"work_x": "work"}, inplace=True)
        data.rename(columns={"subject_x": "subject 1"}, inplace=True)
        data.rename(columns={"subject_y": "subject 2"}, inplace=True)
        data.rename(columns={"book bibliographic info_x": "book 1 info"}, inplace=True)
        data.rename(columns={"book bibliographic info_y": "book 2 info"}, inplace=True)
        data.rename(columns={"page_x": "page 1"}, inplace=True)
        data.rename(columns={"page_y": "page 2"}, inplace=True)
        data.rename(columns={"ref_x": "ref"}, inplace=True)
        data = data.astype(str).groupby('work').agg(
            {'subject 1': '; '.join, 'subject 2': '; '.join, 'page 1': ','.join, 'page 2': ','.join, 'ref': ','.join,
             'author': 'first', 'book 1 info': 'first', 'book 2 info': 'first', }).reset_index()

        data = data.groupby(["author", "work", "subject 1", "book 1 info", "page 1", "book 2 info", "page 2", "ref"])[
            "subject 2"].apply(lambda x: '; '.join(x)).reset_index()
        data = \
            data.groupby(["work", "subject 1", "subject 2", "book 1 info", "page 1", "book 2 info", "page 2", "ref"])[
                "author"].apply(lambda x: ', '.join(x)).reset_index()
        data = \
            data.groupby(["author", "subject 1", "subject 2", "book 1 info", "page 1", "book 2 info", "page 2", "ref"])[
                "work"].apply(lambda x: ', '.join(x)).reset_index()
        data = data.groupby(["author", "work", "subject 1", "subject 2", "page 1", "book 2 info", "page 2", "ref"])[
            "book 1 info"].apply(lambda x: ', '.join(x)).reset_index()
        data = \
            data.groupby(["author", "work", "subject 1", "subject 2", "book 1 info", "book 2 info", "page 2", "ref"])[
                "page 1"].apply(lambda x: ', '.join(x)).reset_index()
        data = \
            data.groupby(["author", "work", "subject 1", "subject 2", "book 1 info", "book 2 info", "page 1", "ref"])[
                "page 2"].apply(lambda x: ', '.join(x)).reset_index()
        data = \
            data.groupby(
                ["author", "work", "subject 1", "subject 2", "book 1 info", "page 1", "book 2 info", "page 2"])[
                "ref"].apply(lambda x: ', '.join(x)).reset_index()
        data = data.groupby(["author", "work", "subject 1", "subject 2", "page 1", "book 2 info", "page 2", "ref"])[
            "book 1 info"].apply(lambda x: ', '.join(x)).reset_index()

        data = data[
            ["author", "work", "ref", "subject 1", "subject 2", "book 1 info", "page 1", "book 2 info", "page 2"]]
        data["ref"] = data["ref"].apply(natural)
        data["ref"] = data["ref"].apply(rehyph)
        data["page 1"] = data["page 1"].str.replace('\\.0', '')
        data["page 2"] = data["page 2"].str.replace('\\.0', '')
        data["book 1 info"] = data["book 1 info"].str.replace('\\.0', '')
        data["book 2 info"] = data["book 2 info"].str.replace('\\.0', '')
        data["page 1"] = data["page 1"].apply(natural)
        data["page 2"] = data["page 2"].apply(natural)
        data["page 1"] = data["page 1"].apply(hyph)
        data["page 2"] = data["page 2"].apply(hyph)
        data['subject 1'] = data['subject 1'].str.split().apply(lambda x: OrderedDict.fromkeys(x).keys()).str.join(', ')
        data['subject 2'] = data['subject 2'].str.split().apply(lambda x: OrderedDict.fromkeys(x).keys()).str.join(', ')
        data['subject 1'] = data['subject 1'].str.replace(', ', ' ')
        data['subject 2'] = data['subject 2'].str.replace(', ', ' ')

        data = data[
            ["author", "work", "ref", "subject 1", "subject 2", "book 1 info", "page 1", "book 2 info", "page 2"]]
        data['book 1 info'] = data['book 1 info'].map(BOOKDICT)
        data['book 2 info'] = data['book 2 info'].astype(str)
        data['book 2 info'] = data['book 2 info'].map(BOOKDICT)

        length_data = len(data.ref)
        Listkk = Listkk + Listbb3
    if option != "and":
        bb = data.loc[:, "subject"]
        bb1 = bb.drop_duplicates(keep="first")
        Listkk = bb1.tolist()
        data = data.sort_values(by=["author", "work", "ref"])
        data['page'] = data['page'].astype(str)
        data['page'] = data['page'].str.replace('\\.0', '')
        data['book bibliographic info'] = data['book bibliographic info'].str.replace('\\.0', '')
        data = pd.merge(data, BOOKPD, on=['book bibliographic info'], how="left")
        data['book bibliographic info'] = data['titleref']
        data = data.drop(["titleref"], axis=1)
        data['page'] = "<a href=https://books.google.co.il/books?id=" + data['gcode'] + \
                       "&lpg=PP1&pg=PA" + data['page'] + "#v=onepage&q&f=false>" + data['page'] + "</a>"
        data = data.drop(["gcode"], axis=1)
        data['ref'] = data['ref'].astype(str)
        data = data[~data["ref"].str.contains("00:00:00", na=False)]
        validated = data
        validated = validated.drop_duplicates(keep="first")
        validated["joined"] = validated["work"].map(str) + " " + validated["ref"]
        validated = validated.astype(str).groupby('joined').agg \
            ({'page': ','.join, 'book bibliographic info': '#'.join, 'ref': ','.join, \
              'work': 'first', 'author': 'first', 'subject': '#'.join}).reset_index()
        validated['book bibliographic info'] = validated['book bibliographic info'].astype(str)
        validated = validated[validated['book bibliographic info'].str.contains('#', na=False)]
        validated["subject"] = validated["subject"].apply(dup)
        validated['book bibliographic info'] = validated["book bibliographic info"].apply(dup)
        validated = validated.drop(['joined'], axis=1)
        if len(validated) != 0:
            validated["joined"] = validated["work"].map(str) + " " + validated["subject"]
            validated = validated.astype(str).groupby('joined').agg \
                ({'ref': ','.join, 'work': 'first', 'author': 'first', 'subject': '#'.join, \
                  'book bibliographic info': '#'.join, 'page': 'first'}).reset_index()
            validated["subject"] = validated["subject"].apply(dup)
            validated['book bibliographic info'] = validated["book bibliographic info"].apply(dup)
            validated = validated.drop(['joined'], axis=1)
            validated = validated.sort_values(by=["work", "ref"])
            validated = validated[["author", "work", "ref", "subject", 'book bibliographic info', 'page']]
            validated = validated.drop_duplicates(keep="first")
            length_validated = len(validated.ref)
            validated["ref"] = validated["ref"].apply(natural)
            validated["ref"] = validated["ref"].apply(rehyph)
            validated = validated.sort_values(by=["author", "work", "ref"])
            validated = validated.reset_index(drop=True)
            highly_validated = validated[validated['book bibliographic info'].str.contains(',', na=False)]
            if len(highly_validated) != 0:
                highly_validated = highly_validated.sort_values(by=["author", "work", "ref"])
                length_highly_validated = len(highly_validated.ref)
                highly_validated = highly_validated.reset_index(drop=True)
        if len(data.index) != 0:
            data = data.groupby(["author", "work", "subject", 'book bibliographic info', 'page']) \
                ['ref'].apply(lambda x: ', '.join(x)).reset_index()
            data = data.groupby(["author", "work", "ref", 'book bibliographic info', 'page']) \
                ['subject'].apply(lambda x: ', '.join(x)).reset_index()
            data = data.groupby(["author", "work", "ref", 'page', 'subject']) \
                ['book bibliographic info'].apply(lambda x: ', '.join(x)).reset_index()
            data = data.sort_values(by=["work", "ref"])
            data = data[["author", "work", "ref", "subject", 'book bibliographic info', 'page']]
            length_data = len(data.ref)
        else:
            empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"
    try:
        data = data.sort_values(by=["author", "work", "ref"])
        length_data = len(data.ref)
    except:
        empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"
    if len(data.index) == 0:
        empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"

    else:
        data["ref"] = data["ref"].apply(natural)
        data["ref"] = data["ref"].apply(rehyph)
        if option != "and":
            data = data.groupby(["author", "work", "subject", 'book bibliographic info', 'ref'])['page'].apply(
                lambda x: ', '.join(x)).reset_index()
            data["page"] = data["page"].apply(hyph)
            data = data[["author", "work", "ref", "subject", 'book bibliographic info', 'page']]
        data = data.drop_duplicates(keep="first")
        if fulltext != "f":
            if (len(data) < 100) and (len(data != 0)):
                data = crn(data)
                data = crneng(data)
                if option != "and":
                    data["results"] = data["author"] + ", <i>" + data["work"] + "</i>, " + data[
                        "ref"] + SIM_SUBJECT_TEXT_TAG \
                                      + data["subject"] + BOOK_TAG_TEXT + data[
                                          "book bibliographic info"] + " on pages: " + data["page"] + \
                                      "<table><tr><td style='min-width:600px'>" + data["refcite"] + "</td><td>" + data[
                                          "refengcite"] + "</td></tr></table>"
                    data = data[['results']]
                if option == "and":
                    data["results"] = data["author"] + ", <i>" + data["work"] + "</i>, " + data[
                        "ref"] + SIM_SUBJECT_TEXT_TAG \
                                      + data["subject 1"] + "<br>" + data["subject 2"] + "<br><br>"
                data["book 1"] = data["book 1 info"] + ", " + data["page 1"]
                data["book 2"] = data["book 2 info"] + ", " + data["page 2"]
                data = data[['results', 'refcite', 'refengcite', 'book 1', 'book 2']]
            data.rename(columns={
                "refcite": "full text.............................................................................."},
                inplace=True)
            data.rename(columns={
                "refengcite": "English translation.............................................................................."},
                inplace=True)
        if len(validated) != 0:
            validated = crn(validated)
            validated = crneng(validated)
            # validated["refcite"] = validated["refcite"]
            # validated["refengcite"] = validated["refengcite"]
            if option != "and":
                validated["results"] = validated["author"] + ", <i>" + validated["work"] + "</i>, " + validated["ref"] \
                                       + SUBJECT_TAG_TEXT + \
                                       +validated["subject"] + BOOK_TAG_TEXT + validated["book bibliographic info"] \
                                       + ", pages: " + validated[
                                           "page"] + "</span><table><tr><td style='min-width:600px'>" + validated \
                                           ["refcite"] + "</td><td>" + validated["refengcite"] + "</td></tr></table>"
                validated = validated[['results']]
        if option == "and":
            validated["results"] = validated["author"] + ", <i>" + validated["work"] + "</i>, " + validated["ref"] \
                                   + SIM_SUBJECT_TEXT_TAG + validated["subject 1"] + "<br>" + validated[
                                       "subject 2"] + "<br><br>"
            validated["book 1"] = validated["book 1 info"] + ", " + validated["page 1"]
            validated["book 2"] = validated["book 2 info"] + ", " + validated["page 2"]
            validated = validated[['results', 'refcite', 'refengcite', 'book 1', 'book 2']]
        validated.rename(columns={
            "refcite": "full text.............................................................................."},
            inplace=True)
        validated.rename(columns={
            "refengcite": "English translation.............................................................................."},
            inplace=True)
    if len(highly_validated) != 0:
        highly_validated = crn(highly_validated)
        highly_validated = crneng(highly_validated)
        highly_validated["refcite"] = highly_validated["refcite"]
        highly_validated["refengcite"] = highly_validated["refengcite"]
        if option != "and":
            highly_validated["Index1"] = highly_validated.index
            highly_validated["Index1"] = highly_validated["Index1"] + 1
            highly_validated["results"] = highly_validated["Index1"].astype(str) + ". " + highly_validated["author"] \
                                          + ", <i>" + highly_validated["work"] + "</i>, " + highly_validated["ref"] + \
                                          SUBJECT_TAG_TEXT + highly_validated["subject"] + BOOK_TAG_TEXT + \
                                          highly_validated["book bibliographic info"] + ", pages: " + highly_validated[
                                              "page"] + "</span>"
            highly_validated = highly_validated[['results', 'refcite', 'refengcite']]
        if option == "and":
            highly_validated["results"] = highly_validated["author"] + ", <i>" + highly_validated["work"] \
                                          + "</i>, " + highly_validated["ref"] + SUBJECT_TAG_TEXT + highly_validated \
                                              ["subject 1"] + "<br>" + highly_validated["subject 2"] + "<br><br>"
            highly_validated["book 1"] = highly_validated["book 1 info"] + ", " + highly_validated["page 1"]
            highly_validated["book 2"] = highly_validated["book 2 info"] + ", " + highly_validated["page 2"]
            highly_validated = highly_validated[['results', 'refcite', 'refengcite', 'book 1', 'book 2']]
        highly_validated.rename(columns={
            "refcite": "full text.............................................................................."},
            inplace=True)
        highly_validated.rename(columns={
            "refengcite": "English translation.............................................................................."},
            inplace=True)

else:
    if option != "and":
        data["results"] = "<b>" + data["author"] + ", <i>" + data["work"] + "</i>, " + data["ref"] + \
                          "</b><span style='padding-left: 50px; display:block'><br>&nbsp;&nbsp;&nbsp;Tagged \
                          with subjects: " + data["subject"] + BOOK_TAG_TEXT + \
                          data["book bibliographic info"] + ", pages: " + data["page"] + "</span>"
        data = data[['results']]
        if len(validated) != 0:
            validated["Index1"] = validated.index
            validated["Index1"] = validated["Index1"] + 1
            validated["results"] = "<b>&emsp;" + validated["Index1"].astype(str) + ". " + validated[
                "author"] + ", <i>" + validated["work"] + "</i>,\
					" + validated["ref"] + "</b>" + SUBJECT_TAG_TEXT + validated["subject"] \
                                   + BOOK_TAG_TEXT + validated["book bibliographic info"] + ", pages: " + validated[
                                       "page"] + "</span>"
            validated = validated[['results']]
        if len(highly_validated) != 0:
            if len(highly_validated) < 50:
                try:
                    highly_validated = crn(highly_validated)
                    highly_validated = crneng(highly_validated)
                    highly_validated["Index1"] = highly_validated.index
                    highly_validated["Index1"] = highly_validated["Index1"] + 1
                    highly_validated["results"] = "<b>&emsp;" + highly_validated["Index1"].astype(str) \
                                                  + ". " + highly_validated["author"] + ", <i>" + highly_validated[
                                                      "work"] \
                                                  + "</i>, " + highly_validated["ref"] \
                                                  + "</b>" + SUBJECT_TAG_TEXT + highly_validated[
                                                      "subject"] + BOOK_TAG_TEXT \
                            "+highly_validated["
                    book
                    bibliographic
                    info
                    "]+", pages: "\
					+highly_validated["
                    page
                    "]+
                    "</span><br><br><table style='font-family:Palatino'><td style='min-width:600px;font-family:Palatino'>" \
                    + highly_validated["refcite"] + "</td><td>" + highly_validated["refengcite"] + "</td></tr></table>"
            except:
            highly_validated["Index1"] = highly_validated.index
            highly_validated["Index1"] = highly_validated["Index1"] + 1
            highly_validated["results"] = "<b>&emsp;" + highly_validated["Index1"].astype(str) + \
                                          ". " + highly_validated["author"] + ", <i>" + highly_validated[
                                              "work"] + "</i>, " + \
                                          highly_validated["ref"] + "</b>" + SUBJECT_TAG_TEXT + highly_validated[
                                              "subject"] \
                                          + BOOK_TAG_TEXT + highly_validated["book bibliographic info"] \
                                          + ", pages: " + highly_validated["page"] + "</span><br><br>"
    else:
        highly_validated["Index1"] = highly_validated.index
        highly_validated["Index1"] = highly_validated["Index1"] + 1
        highly_validated["results"] = "<b>&emsp;" + highly_validated["Index1"].astype(str) + \
                                      ". " + highly_validated["author"] + ", <i>" + highly_validated["work"] + "</i>, " \
                                      + highly_validated["ref"] + "</b>" + SUBJECT_TAG_TEXT + highly_validated[
                                          "subject"] \
                                      + BOOK_TAG_TEXT + highly_validated["book bibliographic info"] \
                                      + ", pages: " + highly_validated["page"] + "</span><br><br>"
    highly_validated = highly_validated[['results']]
else:
data["book 1"] = data["book 1 info"] + ", " + data["page 1"]
data["book 2"] = data["book 2 info"] + ", " + data["page 2"]
data["results"] = data["author"] + ", <i>" + data["work"] + "</i>, " + data["ref"] + SIM_SUBJECT_TEXT_TAG \
                  + data["subject 1"] + "<br>" + data["subject 2"] + BOOK_TAG_TEXT \
                  + data["book 1"] + "; " + data["book 2"]
data = data[['results']]
if len(highly_validated) != 0:
    highly_validated["Index1"] = highly_validated.index
    highly_validated["Index1"] = highly_validated["Index1"] + 1
    highly_validated["results"] = highly_validated["Index1"].astype(str) + ". " + highly_validated["author"] \
                                  + ", <i>" + highly_validated["work"] + "</i>, " + highly_validated[
                                      "ref"] + SIM_SUBJECT_TEXT_TAG \
                                  + highly_validated["subject 1"] + "<br>" + highly_validated["subject 2"] + "<br><br>"
    highly_validated["book 1"] = highly_validated["book 1 info"] + ", " + highly_validated["page 1"]
    highly_validated["book 2"] = highly_validated["book 2 info"] + ", " + highly_validated["page 2"]
    highly_validated = highly_validated[['results', 'refcite', 'refengcite', 'book 1', 'book 2']]

return render_template('index.html', ccs=ccs, ccs1=ccs1, tablev=validated.to_html(escape=False, index=False), \
                       step="choose_upper", l=l, tablev1=highly_validated.to_html(escape=False, index=False),
                       lengthvv1=length_highly_validated, \
                       tablek=data.to_html(escape=False), YYY=YYY, fulltext=fulltext, cs=cs, ce=ce, lang=lang,
                       author=author, \
                       work=work, ref=ref, lengthkk=length_data, Listkk=Listkk, empty=empty, lengthvv=length_validated)

return '''<form method="POST">
<style type="text/css">
  <!--
  .tab { margin-left: 50px; line-height:25px}
  .spacing {margin-bottom:1.5em}
  font-family {"Times New Roman", "Times New Roman"}
  -->


.row {
  display: flex;
}

.column {
  flex: 50%;
}

  </style>


<html>
<head>
<meta name="google-site-verification" content="wFqE_o03KyMrIIsHQASE-Rl3LG4cbfGMzq0vBc7wgTo" />
<body style="font-family:Calibri;"></body>
<title> The Ancient Mediterranean Religions Index Database </title>
</head>

<style type="text/css">
#bottombox{
position:static;
left:0%;
width:100%;
height:80px;
margin-top:0px;
margin-left:0px;
background:lightblue;

input[type=submit] {
  border: none;
  height: 100px;
  width: 200px
}
}
#blackbox{
position:absolute;
top:0%;
left:0%;
width:100%;
height:100px;
margin-top:0px;
margin-left:0px;
background:lightblue;
}
p{
text-align:center;
font-size:20px;
line-height:10px;
margin:0px;
}

</style>
</head>
<body>

<div id="blackbox"><p><br><br><br><br><b>Tiresias: The Ancient Mediterranean Religions Source Database</b><br><br> </p></div>
</body>
                  <br><br><br><br><br><br><div align="center">
&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp

<br>



<font size=+1>
<b>Enter a keyword to search</b><br>
 <small>if you're not sure what to search for, leave form empty and click submit for a random subject </small><br><br>
<input type="text" name="c" style="width: 220px; height: 40px;" /> <br>
<br>optional: add another keyword<br>
<input type="radio" name="option" id="and" value="and"> and </input><br>
<input type="text" name="d" style="width: 220px; height: 40px;" /><br><br>
</font></div>

<br>
<p>
<div id="bottombox"><p>
                  <div align="center">
                  <br>
                  <input type="submit" value="Submit" style="width: 120px; height: 20px;" /  ><br>
                  </div>
</p></div>
                  </p>
<br>
<div class="row">
    <div class="column">


                  <li>Leave form empty and click "submit" to search for a random subject</li>
                  <li>for a list of subjects, go <a href="http://tiresias.haifa.ac.il/subjects">here</a>; for a list of book indices included, go <a href="http://tiresias.haifa.ac.il/biblio">here</a></li>
                  <li>The database includes general subjects, ideas, names and places, almost all in English; the subjects are the same you would find in a good subject index of a book.</li>
                  <li>The database currently includes 4,358,083 references indexed by 46,478 subjects.</li>
</div>

<div class="column">
                  The database is in its early stages of development, with many errors. Please use with caution. References are to texts between the 8th century BCE and the 8th century CE.
                  <br>The site was built and is maintained by Moshe Blidstein of the General History Department and the Haifa Center for Mediterrean History, University of Haifa. For information and suggestions, please contact mblidstei@univ.haifa.ac.il. <br>
                  <br>If you would like to receive updates on the development of the project, please enter your email and click "submit" above: <input type="text" name="email"></div></div>
                  <br></font>
              </form>'''
