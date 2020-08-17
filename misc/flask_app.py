import base64
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
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

app = Flask(__name__)
app.debug = True

titles = pd.read_csv("/home/moblid/mysite/titlesa.csv", encoding='utf-8')
urndata = ("/home/moblid/mysite/urns1.csv")
urnpd = pd.read_csv(urndata)
crnpd = pd.read_csv("/home/moblid/mysite/crn2.csv")
crnpd["author"] = crnpd["author"].str.lower()
crnpd["work"] = crnpd["work"].str.lower()
crnengpd = pd.read_csv("/home/moblid/mysite/crneeng.csv")
bookpd = pd.read_csv("/home/moblid/mysite/bookreferences2.csv")
bookpd["book bibliographic info"] = bookpd["book bibliographic info"].astype(str)
bookdict = dict(zip(bookpd['book bibliographic info'], bookpd['titleref']))
synonyms = []
mar = []
zar = []
bar = []
longlist = []
yyy = ""

def crn(unciteddata):
    unciteddata["author"] = unciteddata["author"].str.lower()
    unciteddata["work"] = unciteddata["work"].str.lower()
    crnmerge = pd.merge(unciteddata, crnpd, on=["author","work"], how="left")
    if (len(crnmerge.columns))>8:
      if option=="and":
        crnmerge = crnmerge[["author","work","ref","refcite","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2"]]
    else:
      crnmerge = crnmerge[["author","work","ref", "refcite", "subject",'book bibliographic info', 'page']]
    crnmerge["ref"] = crnmerge["ref"].astype(str)
    crnmerge["refcite"] = crnmerge["refcite"].astype(str)
    #crnmerge["ref"]  = np.where(crnmerge["refcite"].astype(str).str.contains('nan'), crnmerge["ref"], crnmerge["refcite"])
    #crnmerge['ref'] = crnmerge['refcite']
    for a in range (len(crnmerge)):
      refd = str(crnmerge.iloc[a, 3])
      refc = str(crnmerge.iloc[a, 2])
      if refd[1:3] == "ho":
        fltxt = pd.read_csv(refd, encoding='utf8')
        if ("," in refc) or ("-" in refc) :
          listrefdd = []
          if "," in refc:
            refc = refc.replace(", ",",")
            listrefc = refc.split(",")
            for z in range(0,len(listrefc)):
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
            listrefee =[]
            for x in range(0, len(listrefdd)):
              opp = listrefdd[x]
              if opp.count(".") == 2:
                cut = str(opp.split('.',2)[0])+str(opp.split('.',2)[1])
                listrefee.append(cut)
              else:
                listrefee.append(opp)
            listrefdd = listrefee
          fltxt['ref'] = fltxt['ref'].astype(str)
          listreftext = []
          listrefdd_df = pd.DataFrame({"a":listrefdd})
          fltxta = fltxt.loc[fltxt['ref'].isin(listrefdd_df["a"])]
          fltxta["results"] = fltxta["ref"]+". "+fltxta["text"]
          listreftext = fltxta['results'].values.tolist()
          listreftext = natsorted(listreftext)
          if len(listreftext) == 0:
            strreflink = listrefdd
          else:
            strreflink = " ".join(listreftext)
            strreflink = strreflink.replace("\r\n","<br>")
            strreflink = strreflink.replace("\\r\\n","<br>")
          crnmerge.iloc[a, 3] = strreflink
        else:
          refg=refc
          if "annal" in refd:
            refg = refg.split('.',2)[0]+"."+refg.split('.',2)[1]
          fltxt['ref'] = fltxt['ref'].astype(str)
          listreftext = []
          fltxta = fltxt.loc[fltxt['ref']==refg]
          fltxta["results"] = fltxta["ref"]+". "+fltxta["text"]
          listreftext = fltxta['results'].values.tolist()
          if len(listreftext) == 0:
            strreflink = str(refg)
          else:
            strreflink = " ".join(listreftext)
          crnmerge.iloc[a, 3] = strreflink
      elif refd[0:2] == "ht":
        if ("," in refc):
          if "tlg0059" in refd:
            refc = refc.replace("[a-z]","")
          refc = refc.replace(", ",",")
          refc = refc.replace(", ",",")
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
                res2 = res2.split('"he":',1)[1]
                #res2 = res2.split('"]',1)[0]
                res2 = res2.split(', "he',1)[0]
                res2 = res2.split(', "is',1)[0]
                res2 = res2.split(', "version',1)[0]
              if len(res2)>2000:
                res2 = res2[0:2000]
              res2 = res2.replace("^', '","")
              res2 = res2.replace("\n\n\n","\n")
              res2 = res2.replace("\n\n","\n")
              res2 = res2.replace("\n"," ")
              res2 = res2.replace("\t","")
              listreftext.append(listrefc[x]+".")
              listreftext.append(res2)
              listreftext.append("<br/>")
            except:
              listreftext.append("empty")
          strreflink = str(listreftext)
          strreflink = str(listreftext)
          strreflink = strreflink[2:-2]
          strreflink = strreflink.replace("', '","")
          crnmerge.iloc[a, 3] = strreflink
        else:
          try:
            if "tlg0059" in refd:
              #refc = refc.replace("c-d","")
              refc = re.sub(r'[a-z]-[a-z]','',refc)
              refc = refc.replace("[a-z]","")
            if "stoa0275" in refd:
              refc = refc.split('.',1)[0]
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
              res2 = res2.split('"he":',1)[1]
              #res2 = res2.split('"]',1)[0]
              res2 = res2.split(', "he',1)[0]
              res2 = res2.split(', "is',1)[0]
              res2 = res2.split(', "version',1)[0]
            if len(res2)>2000:
              res2 = res2[0:2000]
            res2 = res2.replace("\n\n\n","\n")
            res2 = res2.replace("\n\n","\n")
            res2 = res2.replace("\n"," ")
            #res2 = res2.replace("xxx","<br/>")
            res2 = res2.replace("\t","")
            crnmerge.iloc[a, 3] = res2
          except:
            crnmerge.iloc[a, 3] = refd
      else:
        crnmerge.iloc[a, 3] = refd
    #crnmerge = crnmerge.drop('encoding', 1)
    citeddata = crnmerge
    return(citeddata)

def crneng(unciteddata):
    unciteddata["author"] = unciteddata["author"].str.lower()
    unciteddata["work"] = unciteddata["work"].str.lower()
    crnengpd["author"] = crnengpd["author"].str.lower()
    crnengpd["work"] = crnengpd["work"].str.lower()
    crnengmerge = pd.merge(unciteddata, crnengpd, on=["author","work"], how="left")
    if (len(crnengpd.columns))>8:
      crnengmerge = crnengmerge[["author","work","ref","refcite","refengcite","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2"]]
    else:
      crnengmerge = crnengmerge[["author","work","ref", "refcite","refengcite", "subject",'book bibliographic info', 'page']]
    crnengmerge["ref"] = crnengmerge["ref"].astype(str)
    crnengmerge["refengcite"] = crnengmerge["refengcite"].astype(str)
    for a in range (len(crnengmerge.index)):
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
                if listrefc[x][-1]=="a" or listrefc[x][-1]=="b" or listrefc[x][-1]=="c" or listrefc[x][-1]=="d" or listrefc[x][-1]=="e":
                  listrefc[x] = listrefc[x][:-1]
              refe = refd.replace("linkref", listrefc[x])
              res = requests.get(refe)
              res.encoding = 'utf-8'
              if "sefaria" in refd:
                res.encoding = 'unicode-escape'
              res2 = res.text
              if len(res2)>3000:
                res2 = res2[0:3000]
              if "went wrong" in res2:
                res2 = "text not available"
              if "sefaria" in refd:
                res2 = res2.split('"text":',1)[1]
                #res2 = res2.split(']',1)[0]
                res2 = res2.split(', "next"',1)[0]
                res2 = res2.split(', "he"',1)[0]
                res2 = res2.split(', "heT',1)[0]
                res2 = res2.split(', "heV',1)[0]
                res2 = res2.split(', "titleV',1)[0]
                res2 = res2.split(', "is[A-Z]',1)[0]
                res2 = res2.split(', "isD',1)[0]
                res2 = res2.split(', "isC',1)[0]
                res2 = res2.split(', "versi',1)[0]
                res2 = res2.split('sectionR',1)[0]
                res2 = res2.split('ref',1)[0]
                res2 = res2.replace("\[\"","")
                res2 = res2.replace("\"\]","")
                res2 = res2.replace("\", \""," ")
                res2 = res2.replace("\",\""," ")
                res2 = res2.replace("$[\"","")
                res2 = res2.replace("\"]^","")
              res2 = res2.replace("\n\n\n","\n")
              res2 = res2.replace("\n\n","\n")
              res2 = res2.replace("\n"," ")
              res2 = res2.replace("\t","")
              listreftext.append(listrefc[x]+".")
              listreftext.append(res2)
              listreftext.append("<br/>")
            except:
              listreftext.append("empty")
          listreftext = natsorted(listreftext)
          strreflink = str(listreftext)
          strreflink = strreflink[2:-2]
          strreflink = strreflink.replace("', '","")
          crnengmerge.iloc[a, 4] = strreflink
        else:
          try:
            if "tlg0059" in refd:
              refc = refc.replace("[a-z]","")
            refd = refd.replace("linkref", refc)
            res = requests.get(refd)
            res.encoding = 'utf-8'
            if "sefaria" in refd:
              res.encoding = 'unicode-escape'
            res2 = res.text
            if "sefaria" in refd:
              res2 = res2.split('"text":',1)[1]
              #res2 = res2.split(']',1)[0]
              res2 = res2.split(', "next"',1)[0]
              res2 = res2.split(', "he"',1)[0]
              res2 = res2.split(', "heT',1)[0]
              res2 = res2.split(', "heV',1)[0]
              res2 = res2.split(', "heE',1)[0]
              res2 = res2.split(', "titleV',1)[0]
              res2 = res2.split(', "isC',1)[0]
              res2 = res2.split(', "isD',1)[0]
              res2 = res2.split(', "vers',1)[0]
              res2 = res2.replace("\[\"","")
              res2 = res2.replace("\"\]","")
              res2 = res2.replace("\", \""," ")
              res2 = res2.replace("\",\""," ")
            if "went wrong" in res2:
                res2 = "English translation unavailable"
            res2 = res2.replace("\n"," ")
            res2 = res2.replace("\t","")
            crnengmerge.iloc[a, 4] = res2
          except:
            crnengmerge.iloc[a, 4] = refd
      elif refd[0:2] == "xx":
        refd = refd.replace("xx","")
        try:
            fltxt = pd.read_csv(refd, encoding='utf8')
            refc = refc.replace("\. ",".")
            if ("," in refc) or ("-" in refc) :
              listrefdd = []
              if "," in refc:
                  refc = refc.replace(", ",",")
                  listrefc = refc.split(",")
                  for z in range(0,len(listrefc)):
                        if "-" in listrefc[z]:
                          lz = listrefc[z]
                          dop = hyphenate_b(lz)
                          listrefdd.extend(dop)
                        else:
                          listrefdd.append(listrefc[z])
              elif "," not in refc:
                  if "-" in refc:
                    listrefdd = hyphenate_b(refc)
              #listrefd = [",".join(i) for i in listrefc]
              #listrefg = [str(i) for i in listrefd]
              if "annal" in refd:
                  listrefee =[]
                  for x in range(0, len(listrefdd)):
                    opp = listrefdd[x]
                    if opp.count(".") == 2:
                        cut = str(opp.split('.',2)[0])+str(opp.split('.',2)[1])
                        listrefee.append(cut)
                    else:
                        listrefee.append(opp)
                  listrefdd = listrefee
              fltxt['ref'] = fltxt['ref'].astype(str)
              listreftext = []
              listrefdd_df = pd.DataFrame({"a":listrefdd})
              fltxta = fltxt.loc[fltxt['ref'].isin(listrefdd_df["a"])]
              fltxta["results"] = fltxta["ref"]+". "+fltxta["text"]
              listreftext = fltxta['results'].values.tolist()
              if len(listreftext) == 0:
                  strreflink = listrefdd
              else:
                  strreflink = " ".join(listreftext)
                  strreflink = strreflink.replace("\r\n","<br>")
                  strreflink = strreflink.replace("\\r\\n","<br>")
              crnengmerge.iloc[a, 4] = strreflink
            else:
              refg=refc
              fltxt['ref'] = fltxt['ref'].astype(str)
              listreftext = []
              fltxta = fltxt.loc[fltxt['ref']==refg]
              fltxta["results"] = fltxta["ref"]+". "+fltxta["text"]
              listreftext = fltxta['results'].values.tolist()
              if len(listreftext) == 0:
                  strreflink = str(refg)
              else:
                  strreflink = " ".join(listreftext)
                  strreflink = strreflink.replace("\n","")
              crnengmerge.iloc[a, 4] = strreflink
        except:
            crnengmerge.iloc[a, 4] = "full text problem"

      else:
        crnengmerge.iloc[a, 4] = "ooo"
    crnengmerge["author"] = crnengmerge["author"].str.title()
    crnengmerge["work"] = crnengmerge["work"].str.title()
    crnengmerge["author"] = crnengmerge["author"].str.replace("Of","of")
    citeddata = crnengmerge
    return(citeddata)

def hyphenate_b(x):#the same idea like def:hyphenated but for references which may be of a more complicated format, e.g., 1.3-5, which should become 1.3, 1.4, 1.5
    rr = []
    h = []
    m = str(x)
    a, b = m.split("-")
    try:
        if "." in a:
            a1, a2 = a.split(".")
            b1, b2 = b.split(".")
            a2, b2 = int(a2), int(b2)
            h = list(range(a2, b2+1))
            h = [str(i) for i in h]
            rr = [a1+"."+i for i in h]
            return rr
        else:
            a, b = int(a), int(b)
            h = list(range(a, b+1))
            h = [str(i) for i in h]
            rr = h
            return rr
    except:
        return list(m)


def splitchap(x):
      x = str(x)
      y = x.split('.')[0]
      return y

def hyphenate_a(x):#the same idea like def:hyphenated but for references which may be of a more complicated format, e.g., 1.3-5, which should become 1.3, 1.4, 1.5
    result = []
    out = []
    m = str(x)
    num = m.rfind(".")
    rr = m[num+1:len(m)]
    if '-' in rr:
        a, b = rr.split('-')
        if len(a) >= len(b):
            new = a[0:-(len(b))]+b[-(len(b)):]
            b = new
            a, b = int(a), int(b)
        else:
            a, b = int(a), int(b)
        out.extend(range(a, b+1))
        for jj in range(len(out)):
            out[jj] = str(out[jj])
            uu = m[0:num+1]+out[jj]
            result.append(uu)
    return result

def hyphenate(x):#this takes numbers as they are usually printed(e.g., 1-4, 35-7, 109-11) and expands them (e.g., 1, 2, 3, 4, 35, 36, 37, 109, 110, 111)
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
    						new = a[0:-(len(b))]+b[-(len(b)):]
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

def one():

  texts_subjects = pd.read_csv("/home/moblid/mysite/texts_subjects2.csv", encoding='utf8')
  texts_subjects["C"] = texts_subjects["C"].apply(hyphenate)
  texts_subjects["number of references in database"] = texts_subjects["C"].str.len()
  texts_subjects = texts_subjects[["subject","number of references in database"]]
  subjects_count = texts_subjects.sort_values(by=["number of references in database"],ascending=False)
  subjects_count = subjects_count.head(200)
  lsubjects = len(texts_subjects)
  lrest =  texts_subjects["number of references in database"].sum()


  return render_template('index2.html', subjects_count = subjects_count.to_html(escape=False), lsubjects = lsubjects, lrest = lrest, tables=texts_subjects.to_html(escape=False))

@app.route('/plot', methods=['GET', 'POST'])

def plot():
    import json
    import plotly
    #import plotly.graph_objects as go
    #import networkx as nx

    #G = nx.random_geometric_graph(200, 0.125)


    rng = pd.date_range('1/1/2011', periods=7500, freq='H')
    ts = pd.Series(np.random.randn(len(rng)), index=rng)

    graphs = [
        dict(
            data=[
                dict(
                    x=[1, 2, 3],
                    y=[10, 20, 30],
                    type='scatter'
                ),
            ],
            layout=dict(
                title='first graph'
            )
        ),

        dict(
            data=[
                dict(
                    x=[1, 3, 5],
                    y=[10, 50, 30],
                    type='bar'
                ),
            ],
            layout=dict(
                title='second graph'
            )
        ),

        dict(
            data=[
                dict(
                    x=ts.index,  # Can use the pandas data structures directly
                    y=ts
                )
            ]
        )
    ]


    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    # Add "ids" to each of the graphs to pass up to the client
    # for templating

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='<br>Network graph made with Python',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    figJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('plot.html',
                           ids=ids,fig=fig,
                           graphJSON=graphJSON,figJSON=figJSON)


@app.route("/mysuperplot", methods=["GET"])
def plotView():

    # Generate plot
    #fig = Figure()
    G = nx.Graph()

    G.add_edge('a', 'b', weight=0.6)
    G.add_edge('a', 'c', weight=0.2)
    G.add_edge('c', 'd', weight=0.1)
    G.add_edge('c', 'e', weight=0.7)
    G.add_edge('c', 'f', weight=0.9)
    G.add_edge('a', 'd', weight=0.3)

    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 0.5]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.5]

    pos = nx.spring_layout(G)  # positions for all nodes

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)

    # edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge,
                           width=6)
    nx.draw_networkx_edges(G, pos, edgelist=esmall,
                           width=6, alpha=0.5, edge_color='b', style='dashed')

    # labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

    plt.axis('off')
    fig = plt.show()
    f.savefig("graph.png")
    #axis = fig.add_subplot(1, 1, 1)
    #axis.set_title("title")
    #axis.set_xlabel("x-axis")
    #axis.set_ylabel("y-axis")
    #axis.grid()
    #axis.plot(range(5), range(5), "ro-")

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(f).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    return render_template("image1.html", image=pngImageB64String)


@app.route('/common', methods=['GET', 'POST'])

def common1():
    if request.method == 'POST':
        from collections import Counter
        y1 = []
        x1 = []
        with open('/home/moblid/mysite/stopwords.txt') as f:
            stopwords = f.read().splitlines()
        stop_words = set(stopwords)
        reflist = pd.read_csv("/home/moblid/mysite/reflist.csv")
        reflist1 = reflist[reflist["d"]>1]
        reflist1 = reflist1[["author1","title1"]]
        reflist1["author1"] = reflist1["author1"].astype(str)
        reflist1["works_with_refs_in_more_than_one_book"] = reflist1["author1"].map(str) + " " + reflist1["title1"].astype(str)
        reflist1 = reflist1.groupby(['works_with_refs_in_more_than_one_book']).works_with_refs_in_more_than_one_book.agg('count').to_frame('count').reset_index()
        reflist1 = reflist1.drop_duplicates()
        reflist1 = reflist1.sort_values(by=["count"], ascending=False).reset_index()
        sum1 =  reflist1["count"].sum()
        reflist["subject"] = reflist["subject"].str.lower()
        reflist["subject"] = reflist["subject"].str.replace("/bof/b","")
        reflist["subject"] = reflist["subject"].str.replace("/band/b","")
        reflist["subject"] = reflist["subject"].str.replace("/bas/b","")
        numbera = int(request.form.get('number'))
        books = int(request.form.get('books'))-1
        reflist = reflist[reflist["c"]<numbera]
        reflist = reflist[reflist["d"]>books]
        reflist = reflist.dropna()
        x = str(request.form.get('subject'))
        if x=="random":
            randrow1 = random.randint(0,len(reflist))
            r = (str(reflist.iloc[randrow1,5])).split(",")
            r1 = str(r[random.randint(0,len(r))])
            x=r1
        x1 = x+"s"
        x2 = x+"ing"
        xs = [x,x1,x2]
        reflista = reflist[reflist['subject'].astype(str).str.contains("|".join(xs), na=False)]
        y = ','.join(reflista['subject'].tolist())
        y = y.lower()
        y0 = y.split(",")
        y0 = [x.strip(' ') for x in y0]
        for r in y0:
            if not r in stop_words:
                y1.append(r)
        ii = Counter(y1).most_common(50)
        return render_template('common.html', sum1=sum1, xs=xs, ii = ii,y1=y1,reflist1 = reflist1.to_html(escape=False))

    return '''<form method="POST">
    <font size=+1>
    <b>This tool searches the database for subjects that have the most references in common with the requested subject</b><br><br>
    subject in lowercase (e.g., jesus, book, sword, blood, bread, altar, statue...) : <br> enter the word "random" in the subject box to get a random subject.<br><br><input type="text" name="subject" style="width: 220px; height: 40px;" /> <br>
    number, to filter out very common options (default 50):<br>
    <input type="text" name="number" value = 50 style="width: 220px; height: 40px;" /> <br><br>
    minimum number of books per reference (default 2):<br>
    <input type="text" name="books" value = 2 style="width: 220px; height: 40px;" /> <br><br>

    <input type="submit" value="Submit" style="width: 120px; height: 20px;" /  ><br>

</form>'''

@app.route('/refs', methods=['GET', 'POST'])


def refs():
    bookpd = pd.read_csv("/home/moblid/mysite/bookreferences2.csv", encoding='utf8')
    six1 = pd.read_csv("/home/moblid/mysite/six1.csv", encoding='utf8')
    if request.method == 'POST':
    	pd.set_option('display.max_colwidth', -1)
    	ref=request.form.get('ref')
    	author=request.form.get('author')
    	if author:
    	    author=(str(author).lower())
    	else:
    	    author="anon."
    	work=(str(request.form.get('work'))).lower()
    	joined = author+":"+work
    	six1 = six1[six1["joined"]==joined]
    	a = list(set(six1["number"].values.tolist()))
    	a = a[0]
    	#a = str(request.form.get('c'))
    	db=MySQLdb.connect(host='moblid.mysql.pythonanywhere-services.com',user='moblid',passwd='s4MYP9KSyYkZ6B6',db='moblid$default')
    	sql_for_df = "SELECT * FROM textsa WHERE number="+a
    	df = pd.read_sql_query(sql_for_df , db)

    	if ref:
            if "." in ref:
                df = df[df.ref == ref]
            if "." not in ref:
                df["refchap"] = df["ref"].apply(splitchap)
                df = df[df.refchap == ref]
                df = df.drop(["refchap"], axis=1)
    	df["book bibliographic info"] = df["book bibliographic info"].astype(str)
    	df['book bibliographic info'] = df['book bibliographic info'].str.replace('\\.0', '')
    	bookpd["book bibliographic info"] = bookpd["book bibliographic info"].astype(str)
    	bookpd["gcode"] = bookpd["gcode"].astype(str)
    	df = pd.merge(df,bookpd, on=['book bibliographic info'], how="left")
    	df['book bibliographic info'] = df['titleref']
    	df = df.drop(["titleref"], axis=1)
    	df['gcode'] = df['gcode'].astype(str)
    	df['number'] = df['number'].astype(str)
    	titles['number'] = titles['number'].astype(str)
    	df = pd.merge(df, titles, on="number", how="left")
    	df.rename(columns={"title1": "work"}, inplace=True)
    	df.rename(columns={"author1": "author"}, inplace=True)
    	df = df.drop_duplicates()
    	df['page'] = df['page'].astype(str)
    	df['page'] = df['page'].str.replace('\\.0', '')
    	df['page'] = "<a href=https://books.google.co.il/books?id="+df['gcode']+"&lpg=PP1&pg=PA"+df['page']+"#v=onepage&q&f=false>"+df['page']+"</a>"
    	df = df.drop(["gcode","number","C","file","indexa"], axis=1)
    	df = df.groupby(["work","author","ref", 'book bibliographic info', 'page'])['subject'].apply(lambda x: ', '.join(x)).reset_index()
    	#df = df.to_frame().reset_index()
    	if len(df)>0:
    	    df = crn(df)
    	    df = crneng(df)
    	    df = df.reindex(index=order_by_index(df.index, index_natsorted(df.ref)))
    	return render_template('refs.html', df = df.to_html(escape=False))
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

<title> The Ancient Mediterranean Religions Index Database </title>
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

</head>

<style type="text/css">

#blackbox{
position:absolute;
top:0%;
left:0%;
width:85%;
height:100px;
margin-top:0px;
margin-left:15%;
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
<div class="w3-container">
<div class="w3-sidebar w3-bar-block w3-light-grey w3-card" style="width:15%">
  <br>
  <br>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Home</a>
  <a href="http://tiresias.haifa.ac.il/about" class="w3-bar-item w3-button w3-padding-24">About</a>
  <a href="http://tiresias.haifa.ac.il/network" class="w3-bar-item w3-button w3-padding-24">Network of subjects</a>
  <a href="http://tiresias.haifa.ac.il/biblio" class="w3-bar-item w3-button w3-padding-24">Books included</a>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Search by subject</a>
  <a href="http://tiresias.haifa.ac.il/refs" class="w3-bar-item w3-button w3-padding-24">Search by reference</a>
  <a href="http://tiresias.haifa.ac.il/subjects" class="w3-bar-item w3-button w3-padding-24">Subject list</a>
</div>
</div>

<div style="margin-left:20%; margin-right:20%">

<br><br><br><br><br><br><br>

        <form action="{{ url_for('form_example') }}" method="post">
    If you have a specific reference to ancient text, enter it here to receive a list of subjects relevant to it.<br><br>
    Most author/title styles are accepted. for reference style, please use arabic numerals separated by a period: e.g., 1.5 for book 1, line 5 (or chapter 1, verse 5).
    <br>Leave reference box empty to search for a whole book.
<br><br><br>
    Author:<input type="text" name="author" style="width: 220px; height: 40px; margin-left:88px" /> <br>
    Work:<input type="text" name="work" style="width: 220px; height: 40px;margin-left:100px" /> <br>
    Reference:  <input type="text" name="ref" style="width: 220px; height: 40px;margin-left:59px" /> <br>
    <br><br><input type="submit" value="Submit" style="width: 120px; height: 40px;margin-left:100px" /  ><br>
    </form>'''



@app.route('/refs_map', methods=['GET', 'POST'])


def refs_map():
    bookpd = pd.read_csv("/home/moblid/mysite/bookreferences2.csv", encoding='utf8')
    six1 = pd.read_csv("/home/moblid/mysite/six1.csv", encoding='utf8')
    if request.method == 'POST':
        pd.set_option('display.max_colwidth', -1)
        ref=request.form.get('ref')
        author=request.form.get('author')
        if author:
            author=(str(author).lower())
        else:
            author="anon."
        work=(str(request.form.get('work'))).lower()
        joined = author+":"+work
        six1 = six1[six1["joined"]==joined]
        a = list(set(six1["number"].values.tolist()))
        a = a[0]
        #a = str(request.form.get('c'))
        db=MySQLdb.connect(host='moblid.mysql.pythonanywhere-services.com',user='moblid',passwd='s4MYP9KSyYkZ6B6',db='moblid$default')
        sql_for_df = "SELECT * FROM textsa WHERE number="+a
        df = pd.read_sql_query(sql_for_df , db)
        df = df[df.ref == ref]
        df = df.drop_duplicates()
        x = df["subject"].values.tolist()
        #placeholders= ', '.join(x)
        all_cs = []
        for b in range(0, len(x)):
            c2 = "'"+x[b]+"'"
            query= 'SELECT * FROM texts_subjects WHERE subject='+c2
            texts_subjects1 = pd.read_sql_query(query , db)
            subjects = texts_subjects1['subject'].values.tolist()
            texts_subjects1["C"] = texts_subjects1["C"].apply(hyphenate)
            cs = texts_subjects1['C'].values.tolist()
            all_cs.extend(cs)
        ccs = [item for sublist in all_cs for item in sublist]
        ccs = [str(i) for i  in ccs]
        ccs1 = tuple(ccs)
        sql_for_df = "SELECT * FROM textsa WHERE C IN {}".format(ccs1)
        textsa = pd.read_sql_query(sql_for_df , db)
        textsa["joined"] =  textsa["number"].map(str) + "#" + textsa["ref"]
        textsa["count"] = textsa["joined"].str.count()
        textsa = textsa[textsa["count"]>1]
        return render_template('refs_map.html', df = df.to_html(escape=False), textsa=textsa.to_html(escape=False), all_cs = all_cs,ccs1 = ccs1)

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

<title> The Ancient Mediterranean Religions Index Database </title>
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

</head>

<style type="text/css">

#blackbox{
position:absolute;
top:0%;
left:0%;
width:85%;
height:100px;
margin-top:0px;
margin-left:15%;
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
<div class="w3-container">
<div class="w3-sidebar w3-bar-block w3-light-grey w3-card" style="width:15%">
  <br>
  <br>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Home</a>
  <a href="http://tiresias.haifa.ac.il/about" class="w3-bar-item w3-button w3-padding-24">About</a>
  <a href="http://tiresias.haifa.ac.il/network" class="w3-bar-item w3-button w3-padding-24">Network of subjects</a>
  <a href="http://tiresias.haifa.ac.il/biblio" class="w3-bar-item w3-button w3-padding-24">Books included</a>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Search by subject</a>
  <a href="http://tiresias.haifa.ac.il/refs" class="w3-bar-item w3-button w3-padding-24">Search by reference</a>
  <a href="http://tiresias.haifa.ac.il/subjects" class="w3-bar-item w3-button w3-padding-24">Subject list</a>
</div>
</div>

<div style="margin-left:20%; margin-right:20%">

<br><br><br><br><br><br><br>

        <form action="{{ url_for('form_example') }}" method="post">
    If you have a specific reference to ancient text, enter it here to receive a list of subjects relevant to it.<br><br>
    Most author/title styles are accepted. for reference style, please use arabic numerals separated by a period: e.g., 1.5 for book 1, line 5 (or chapter 1, verse 5).
    <br>Leave reference box empty to search for a whole book.
<br><br><br>
    Author:<input type="text" name="author" style="width: 220px; height: 40px; margin-left:88px" /> <br>
    Work:<input type="text" name="work" style="width: 220px; height: 40px;margin-left:100px" /> <br>
    Reference:  <input type="text" name="ref" style="width: 220px; height: 40px;margin-left:59px" /> <br>
    <br><br><input type="submit" value="Submit" style="width: 120px; height: 40px;margin-left:100px" /  ><br>
    </form>'''



@app.route('/try', methods=['GET', 'POST'])

def tryout():

  artart =[]
  c_art="https://collectionapi.metmuseum.org/public/collection/v1/search?dateBegin=0&dateEnd=800&q=baptism"
  art1 = requests.get(c_art)
  art = art1.text
  art = art.split("objectIDs\":[")[1]
  art = art.split("]}")[0]
  art = art.split("]}")[0]
  art = art.replace("\'", "")
  art = art.split(",")
  for a in range(len(art)):
    art_l = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/objects/"+art[a])
    art_l = art_l.text
    art_l = art_l.split("primaryImageSmall\":\"")[1]
    art_l = art_l.split("jpg")[0]

    artart.append("<img src=\""+art_l+"jpg\"></img>")
  art1 = artart[0]
  art2 = artart[1]

  #artpd = pd.DataFrame({"a":artart})





  return render_template('index3.html', art1=art1, art2=art2, artart=artart)

@app.route('/try1', methods=['GET', 'POST'])

def tryout1():
    a = "animals as oath sacrifices"
    texts_subjects = pd.read_csv("/home/moblid/mysite/texts_subjects1.csv", encoding='utf8')
    texts_subjects = texts_subjects[texts_subjects["subject"].str.contains(a, na=False)]
    subjects = texts_subjects['subject'].values.tolist()

    db=MySQLdb.connect(
    host='moblid.mysql.pythonanywhere-services.com',
    user='moblid',
    passwd='s4MYP9KSyYkZ6B6',
    db='moblid$default')
    #k2 = "'"+str(k[a])+"'"
    a ="'"+str(a)+"'"
    sql_for_df = "SELECT * FROM textsa WHERE subject like"+a
    df = pd.read_sql_query(sql_for_df , db)
    #df1 = df1.append(df)
    #textsa = df1
    #textsa['number'] = textsa['number'].astype(str)
    #titles['number'] = titles['number'].astype(str)
    #textsb = pd.merge(textsa, titles, on="number", how="left")
    #textsb.rename(columns={"title1": "work"}, inplace=True)
    #textsb.rename(columns={"author1": "author"}, inplace=True)
    #textsb = textsb.drop_duplicates()
    #subjects = textsb[["author","work","book bibliographic info","page","ref","subject"]]
    #subjects = subjects.drop_duplicates()
    vv = df



    return render_template("index5.html", step="choose_upper", vv= vv.to_html(escape=False))

@app.route('/books', methods=['GET', 'POST'])
def books():
    df = []
    df = pd.DataFrame({"a":df})
    df1 = []
    df1 = pd.DataFrame({"a":df1})
    db=MySQLdb.connect(
    host='moblid.mysql.pythonanywhere-services.com',
    user='moblid',
    passwd='s4MYP9KSyYkZ6B6',
    db='moblid$default')
    for a in range(1, 2):
        sql_for_df = "SELECT COUNT( * ) FROM textsa WHERE 'book bibliographic info'=1"
        df = pd.read_sql_query(sql_for_df , db)
    vv = df



    return render_template("index6.html", vv= vv.to_html(escape=False))

@app.route("/simple_chart")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('chart.html', values=values, labels=labels, legend=legend)

@app.route('/biblio', methods=['GET', 'POST']) #allow both GET and POST requests
def biblio():
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

<title> The Ancient Mediterranean Religions Index Database </title>
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

</head>

<style type="text/css">

#blackbox{
position:absolute;
top:0%;
left:0%;
width:85%;
height:100px;
margin-top:0px;
margin-left:15%;
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
<div class="w3-container">
<div class="w3-sidebar w3-bar-block w3-light-grey w3-card" style="width:15%">
  <br>
  <br>
  <br>
  <br>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Home</a>
  <a href="http://tiresias.haifa.ac.il/about" class="w3-bar-item w3-button w3-padding-24">About</a>
  <a href="http://tiresias.haifa.ac.il/network" class="w3-bar-item w3-button w3-padding-24">Network of subjects</a>
  <a href="http://tiresias.haifa.ac.il/biblio" class="w3-bar-item w3-button w3-padding-24">Books included</a>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Search by subject</a>
  <a href="http://tiresias.haifa.ac.il/refs" class="w3-bar-item w3-button w3-padding-24">Search by reference</a>
  <a href="http://tiresias.haifa.ac.il/subjects" class="w3-bar-item w3-button w3-padding-24">Subject list</a>
</div>
</div>

<div style="margin-left:20%">

<br><br><br><br><br><br><br><br><br><br>

<b>List of book indices included in the database</b>
<br><br>
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
15. Seim and Okland (2009): Turid Karlsen Seim and Jorunn Økland Seim, eds.,  <i> Metamorphoses: Resurrection, Body and Transformative Practices in Early Christianity</i>. Berlin: De Gruyter, 2009.<br>
16. Boustan, Janssen, Roetzel (2010): Raanan Shaul Boustan, Alex P. Janssen, Calvin J. Roetzel, eds., <i> Violence, Scripture, and Textual Practices in Early Judaism and Christianity</i>. Leiden: Brill, 2010.<br>
17. Nissinen, Uro (2008): Martti Nissinen, Risto Uro, eds., <i> Sacred Marriages: The Divine-Human Sexual Metaphor from Sumer to Early Christianity</i>. Eisenbrauns, 2008.<br>
18. Ramelli (2013): Ilaria Ramelli, <i> The Christian Doctrine of Apokatastasis: A Critical Assessment from the New Testament to Eriugena</i>. Leiden: Brill, 2013.<br>
    19. Perry (2014): Matthew J. Perry, <i> Gender, Manumission, and the Roman Freedwoman</i>. Cambridge: Cambridge University Press, 2014<br>
    20. Nicklas et als. (2010): Tobias Nicklas, Joseph Verheyden, Erik M.M. Eynikel and Florentino Garcia Martinez, eds., <i> Other Worlds and Their Relation to This World: Early Jewish and Ancient Christian Traditions</i>. Leiden: Brill, 2010<br>
    21. Cadwallader (2016): Alan H. Cadwallader, ed., <i> Stones, Bones and the Sacred: Essays on Material Culture and Religion in Honor of Dennis E. Smith</i>. Early Christianity and its literature. SBL Press, 2016<br>
    22. Ando and Rüpke (2006): Clifford Ando and Jörg Rüpke, eds., <i> Religion and Law in Classical and Christian Rome</i>. Steiner: 2006<br>
    23. Demoen and Praet (2009): Kristoffel Demoen and Danny Praet, eds., <i> Theios Sophistes: Essays on Flavius Philostratus' Vita Apollonii</i>. Leiden: Brill: 2009.<br>
    24. Cohen (2010): <i>The Significance of Yavneh and other Essays in Jewish Hellenism</i>. Tubingen: Mohr Siebeck, 2010<br>
    25. Edmonds (2004): Radcliffe G. Edmonds III, <i> Myths of the Underworld Journey: Plato, Aristophanes, and the ‘Orphic’ Gold Tablets</i>. Cambridge: Cambridge University Press, 2004<br>
    26. Gruen (2011): Erich S. Gruen, <i> Rethinking the Other in Antiquity</i>. Princeton: Princeton University Press, 2011<br>
    27. Hubbard (2014): Thomas K. Hubbard (ed.), <i> A Companion to Greek and Roman Sexualities</i>. Malden, MA:  Wiley-Blackwell, 2014<br>
    28. Johnston (2008): Sarah I. Johnston, <i> Ancient Greek Divination</i>. Malden, MA:  Wiley-Blackwell, 2008<br>
    29. Lateiner and Spatharas (2016): Donald Lateiner and Dimos Spatharas, eds., <i> The Ancient Emotion of Disgust</i>. Oxford: Oxford University Press, 2016<br>
    30. Gagarin and Cohen (2005): Michael Gagarin and David Cohen, eds., <i> The Cambridge Companion to Ancient Greek Law</i>. Cambridge: Cambridge University Press, 2005<br>
    31. Bickerman and Tropper (2007): E. J. Bickerman and Amram Tropper, <i> Studies in Jewish and Christian History</i>. Leiden: Brill, 2007. <br>
    32. Hirshman (2009): Marc Hirshman, <i> The Stabilization of Rabbinic Culture, 100 C.E.–350 C.E.: Texts on Education and Their Late Antique Context</i>. Oxford: Oxford University Press, 2009 <br>
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
59. Marzano (2018): Annalisa Marzano and Guy P. R. Métraux, eds., <i> The Roman Villa in the Mediterranean Basin Late Republic to Late Antiquity. </i> Cambridge: Cambridge University Press, 2018.<br>
60. Mcglothlin (2018): Thomas D. McGlothlin, <i> Resurrection as Salvation: Development and Conflict in Pre-Nicene Paulinism</i>. Cambridge: Cambridge University Press, 2018.<br>
61. Tabbernee (2007): William Tabbernee, <i> Fake Prophecy and Polluted Sacraments: Ecclesiastical and Imperial Reactions to Montanism</i>. Leiden: Brill, 2007.<br>
62. Horky (2019): Phillip S. Horky, ed., <i> Cosmos in the Ancient World</i>. Cambridge: Cambridge University Press, 2019<br>
63. Hellholm et al. (2010): David Hellholm, Tor Vegge, Øyvind  Norderval and Christer Hellholm, <i> Ablution, Initiation, and Baptism: Late Antiquity, Early Judaism, and Early Christianity</i>. Berlin: de Gruyter, 2010.<br>
64. Davies (2004): J. P. Davies, <i> Rome's Religious History. Livy, Tacitus and Ammianus on their Gods</i>. Cambridge: Cambridge University Press, 2004.<br>
65. Gwynne (2004): Rosalind W. Gwynne, <i> Logic, Rhetoric and Legal Reasoning in the Qur'an: God's Arguments</i>. London: Routledge, 2009.<br>
67. van den Broek (2013): Roelof van den Broek, <i> Gnostic Religion in Antiquity</i>. Cambridge: Cambridge University Press, 2013.<br>
68. Rupke (2016): Jörg Rüpke, <i> Religious Deviance in the Roman World Superstition or Individuality? </i> Cambridge: Cambridge University Press, 2016.<br>
69. Ando (2013): Clifford Ando, <i> Imperial Ideology and Provincial Loyalty in the Roman Empire</i>. Berkeley: University of California Press, 2013.<br>
70. Rosenblum (2017): Jordan D. Rosenblum, <i> The Jewish Dietary Laws in the Ancient World</i>. Cambridge: Cambridge University Press, 2017.<br>
71. Brodd and Reed (2011): Jeffrey Brodd and Jonathan L. Reed, <i> Rome and Religion: A Cross-Disciplinary Dialogue on the Imperial Cult</i>. Society of Biblical Literature, 2011.<br>
72. Wynne (2019): J. P. F. Wynne, <i> Cicero on the Philosophy of Religion: On the Nature of the Gods and On Divination</i>. Cambridge: Cambridge University Press, 2019.<br>
73. Rojas (2019): Felipe Rojas, <i> The Remains of the Past and the Invention of Archaeology in Roman Anatolia: Interpreters, Traces, Horizons</i>. Cambridge: Cambridge University Press, 2019.<br>
74. Galinsky (2016): Karl Galinsky, <i> Memory in Ancient Rome and Early Christianity</i>. Oxford: Oxford University Press, 2016.<br>
75. Kowalzig (2007): Barbara Kowalzig, <i> Singing for the Gods: Performances of Myth and Ritual in Archaic and Classical Greece</i>. Oxford: Oxford University Press, 2007.<br>
76. Allison (2018): Dale C. Allison, <i> 4 Baruch. Paraleipomena Jeremiou</i>. Berlin: De Gruyter, 2018.<br>
77. Hillier (1993): Richard Hillier, <i> Arator on the Acts of the Apostles: A Baptismal Commentary</i>. Oxford: Oxford University Press, 1993.<br>
78. Shannon-Henderson (2019). Kelly E. Shannon-Henderson, <i> Religion and Memory in Tacitus’ Annals</i>. Oxford: Oxford University Press, 2019.<br>
79. Cain (2016): Andrew Cain, <i> The Greek Historia Monachorum in Aegypto: Monastic Hagiography in the Late Fourth Century</i>. Oxford: Oxford University Press, 2016.<br>
80. McGowan (1999): Andrew Mcgowan, <i> Ascetic Eucharists: Food and Drink in Early Christian Ritual Meals</i>. Oxford: Oxford University Press, 1999.<br>
81. Hickson (1993): Frances V. Hickson, <i> Roman prayer language: Livy and the Aneid of Vergil</i>. Stuttgart: Teubner, 1993.<br>
82. Simmons (1995): Michael B. Simmons, <i>Arnobius of Sicca: Religious Conflict and Competition in the Age of Diocletian</i>. Oxford: Oxford University Press, 1995.<br>
83. Grypeou and Spurling (2009): Emmanouela Grypeou and Helen Spurling, eds., <i>The Exegetical Encounter between Jews and Christians in Late Antiquity</i>. Leiden: Brill, 2009.<br>
84. Keddie (2019): Anthony Keddie, <i>Class and Power in Roman Palestine: The Socioeconomic Setting of Judaism and Christian Origins</i>. Cambridge: Cambridge University Press, 2019.<br>
85. Marmodoro and Prince (2015): Anna Marmodoro and Brian D. Prince, eds., <i>Causation and Creation in Late Antiquity </i>. Cambridge: Cambridge University Press, 2015.<br>
86. Huffman (2014): Carl A. Huffman, <i> A History of Pythagoreanism.  </i> Cambridge: Cambridge University Press, 2014. <br>
87. König (2012): Jason König, <i> Saints and Symposiasts: The Literature of Food and the Symposium in Greco-Roman and Early Christian Culture. </i>. Cambridge: Cambridge University Press, 2012.<br>
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
106. Brouwer (2013): René Brouwer, <i> The Stoic Sage: The Early Stoics on Wisdom, Sagehood and Socrates. </i>Cambridge: Cambridge University Press, 2013.<br>
107. Conybeare (2006): Catherine Conybeare,<i> The Irrational Augustine.</i> Oxford: Oxford University Press, 2006.<br>
108. Burton (2007): Philip Burton, <i> Language in the Confessions of Augustine.</i> Oxford: Oxford University Press, 2007.<br>
109. Cornelli (2013): Gabriele Cornelli, <i> In Search of Pythagoreanism: Pythagoreanism as an Historiographical Category. </i>Berlin: De Gruyter, 2013.<br>
110. Damm (2019): Alex Damm, ed., <i> Religions and Education in Antiquity. Studies in Honor of Michel Desjardins. </i>Leiden: Brill, 2019.<br>
111. Driediger-Murphy and Eidinow (2019): Lindsay G. Driediger-Murphy, Esther Eidinow, eds., <i> Ancient Divination and Experience.</i> Oxford: Oxford University Press, 2019.<br>
112. Frey and Levison (2014): Jörg Frey and John Levison, in collaboration with: Andrew Bowden, eds. <i> The Holy Spirit, Inspiration, and the Cultures of Antiquity Multidisciplinary Perspectives. </i>De Gruyter, 2014.<br>
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
125. Bricault et al (2007): Laurent Bricault, Miguel John Versluys and Paul G.P. Meyboom. <i>Nile into Tiber.Egypt in the Roman World; Proceedings of the IIIrd International Conference of Isis studies, Faculty of Archaeology,Leiden University, May 11-14 2005</i>. Leiden: Brill, 2007.<br>
126. James Clackson et al. (2020): James Clackson et al., <i>Migration, Mobility and Language Contact in and around the Ancient Mediterranean.</i> Cambridge: Cambridge University Press, 2020.<br>
127. Fraade (2011): Steven D. Fraade, <i>Legal Fictions Studies of Law and Narrative in the Discursive Worlds of Ancient Jewish Sectarians and  of Ancient Jewish Sectarians and Sages.</i> Leiden: Brill, 2011.<br>
128. Fletcher (2012): Judith Fletcher, <i>Performing Oaths in Classical Greek Drama.</i> Cambridge: Cambridge University Press, 2012.<br>
129. Eidinow (2007): Esther Eidinow, <i>Oracles, Curses, and Risk Among the Ancient Greeks.</i> Oxford: Oxford University Press, 2007.<br>
130. Fonrobert and Jaffee (2007): <i>Charlotte Elisheva Fonrobert and Martin S. Jaffee, The Cambridge Companion to the Talmud and Rabbinic Literature Cambridge Companions to Religion</i>. Cambridge: Cambridge University Press, 2007.<br>
131. Meinel (2015): Fabian Meinel, <i>Pollution and Crisis in Greek Tragedy</i>. Cambridge, Cambridge University Press, 2015.<br>
132. Grabbe (2010): Lester L. Grabbe, <i>Introduction to Second Temple Judaism: History and Religion of the Jews in the Time of Nehemiah, the Maccabees, Hillel and Jesus</i>. New York: C&C Clark, 2010.<br>
133. Harrison (2006): Simon Harrison, <i>Augustine's Way into the Will: The Theological and Philosophical Significance of De libero arbitrio</i>. Oxford: Oxford University Press, 2006.<br>
134. Flynn (2018): Shawn W. Flynn, <i>Children in Ancient Israel: The Hebrew Bible and Mesopotamia in Comparative Perspective</i>. Oxford: Oxford University Press, 2018.<br>
135. Engberg-Pedersen (2010): Troels Engberg-Pedersen, <i>Cosmology and Self in the Apostle Paul: The Material Spirit</i>. Oxford: Oxford University Press, 2010.<br>
136. Penniman (2017): John David Penniman, <i>Raised on Christian Milk: Food and the Formation of the Soul in Early Christianity</i>. New Haven: Yale University Press, 2017.<br>
137. Moss (2012): Candida R. Moss, <i>Ancient Christian Martyrdom: Diverse Practices, Theologies, and Traditions</i>. New Haven: Yale University Press, 2012.<br>
138. Hahn Emmel and Gotter (2008): Johannes Hahn, Stephen Emmel & Ulrich Gotter, <i>From Temple to Church: Destruction and Renewal of Local Cultic Topography in Late Antiquity</i>. Leiden: Brill, 2008.<br>
139. Gardner (2015): Gregg E. Gardner, <i>The Origins of Organized Charity in Rabbinic Judaism</i>. Cambridge, Cambridge University Press, 2015.<br>
140. Flynn (2018): Shawn W. Flynn, <i>Children in Ancient Israel: The Hebrew Bible and Mesopotamia in Comparative Perspective</i>. Oxford: Oxford University Press, 2018.<br>
141. Dobroruka (2014): Vicente Dobroruka, <i>Second Temple Pseudepigraphy: A Cross-cultural Comparison of Apocalyptic Texts and Related Jewish Literature</i>. Berlin: De Gruyter, 2014.<br>
142. Inwood and Warren (2020): Brad Inwood and James Warren, <i>Body and Soul in Hellenistic Philosophy</i>. Cambridge: Cambridge University Press, 2020.<br>
143. Johnson and Parker (2009): William A. Johnson‏ and Holt N. Parker, ‏<i>Ancient Literacies: The Culture of Reading in Greece and Rome</i>. Oxford: Oxford University Press, 2009.<br>
144. Schaps and Katzoff(2005): David Schaps and Ranon Katzoff, <i>Law in the Documents of the Judaean Desert</i>. Leiden, Brill, 2005.<br>
145. Kaster(2005):,Robert Kaster, <i>Emotion, Restraint, and Community in Ancient Rome</i>. Oxford: Oxford University Press, 2005.<br>
146. Jonquière (2007): Tessel M. Jonquière, <i>Prayer in Josephus Ancient Judaism and Early Christianity</i>. Leiden: Brill, 2007.<br>
147. Jouanna (2012): Jacques Jouanna, <i>Greek Medicine from Hippocrates to Galen. Selected Papers</i>. Leiden, Brill, 2012.<br>
148. Niehoff (2011): Maren R. Niehoff, <i>Jewish Exegesis and Homeric Scholarship in Alexandria</i>. Cambridge: Cambridge University Press, 2011.<br>



</div>
</body>
    </form>'''

@app.route('/network', methods=['GET', 'POST']) #allow both GET and POST requests
def network():
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

<title> The Ancient Mediterranean Religions Index Database </title>
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

</head>

<style type="text/css">


#blackbox{
position:absolute;
top:0%;
left:0%;
width:85%;
height:100px;
margin-top:0px;
margin-left:15%;
background:lightblue;
}
p{
text-align:center;
font-size:20px;
line-height:10px;
margin:0px;
</style>
</head>

<body>
<div id="blackbox"><p><br><br><br><br><b>Tiresias: The Ancient Mediterranean Religions Source Database</b><br><br> </p></div>
</body>
<div class="w3-container">
<div class="w3-sidebar w3-bar-block w3-light-grey w3-card" style="width:15%">
  <br>
  <br>
  <br>
  <br>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Home</a>
  <a href="http://tiresias.haifa.ac.il/about" class="w3-bar-item w3-button w3-padding-24">About</a>
  <a href="http://tiresias.haifa.ac.il/network" class="w3-bar-item w3-button w3-padding-24">Network of subjects</a>
  <a href="http://tiresias.haifa.ac.il/biblio" class="w3-bar-item w3-button w3-padding-24">Books included</a>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Search by subject</a>
  <a href="http://tiresias.haifa.ac.il/refs" class="w3-bar-item w3-button w3-padding-24">Search by reference</a>
  <a href="http://tiresias.haifa.ac.il/subjects" class="w3-bar-item w3-button w3-padding-24">Subject list</a>
</div>
</div>
<br><br><br><br><br><br><br>

<div style="margin-left:20%">
This is an image of the main subjects in the database. <br>
Subjects are arranged by the number of references they share: subjects sharing many references are graphed close to each other, while subjects sharing few references are far apart.<br>
Colors show general clusters of subjects.<br>
Download the image to view at greater resolution.<br><br>
</div>

<div style="margin-left:10%; overflow-x:scroll; overflow-y:scroll">
<img src="/static/large13.1.png" width="1500" height="1500">
</div>
</body>
    </form>'''


@app.route('/about', methods=['GET', 'POST']) #allow both GET and POST requests
def about():
    return '''<form method="POST">


<html>
<head>

<title> The Ancient Mediterranean Religions Index Database </title>
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">


<style type="text/css">

#blackbox{
position:absolute;
top:0%;
left:0%;
width:85%;
height:100px;
margin-top:0px;
margin-left:15%;
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
<div class="w3-container">
<div class="w3-sidebar w3-bar-block w3-light-grey w3-card" style="width:15%">
  <br>
  <br>
  <br>
  <br>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Home</a>
  <a href="http://tiresias.haifa.ac.il/about" class="w3-bar-item w3-button w3-padding-24">About</a>
  <a href="http://tiresias.haifa.ac.il/biblio" class="w3-bar-item w3-button w3-padding-24">Books included</a>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Search by subject</a>
  <a href="http://tiresias.haifa.ac.il/refs" class="w3-bar-item w3-button w3-padding-24">Search by reference</a>
  <a href="http://tiresias.haifa.ac.il/subjects" class="w3-bar-item w3-button w3-padding-24">Subject list</a>
</div>
</div>

<div style="text-align: justify; margin-left:20%; margin-right:5%; line-height:2.2em; margin-bottom:5em">

<br><br><br><br>

Tiresias: The Ancient Mediterranean Religions Source Database provides access to references to ancient texts according to topic, mostly on religion, c. -800 BCE to 800 CE in the Mediterranean area. In some cases, direct access to full text is also available. Topic tagging is based on existing subject indices from scholarly books, allowing highly detailed topic resolution. The site is in development, and currently includes 4,671,592 keyed to 53,097 subjects.
<br>The construction of the database is based on the following method. Many research volumes in ancient history are published with two indices: one for subjects, topics or terms, and one for ancient text references (the latter is also known as an <i>index locorum</i>). Using these indices, each page of the indexed book can be identified as relating to specific subjects as well as specific ancient texts, indicating with a certain probability that these text references can be tagged as related to these subjects. In order to bring this probability closer to 100%, we assess the overlap from a number of books of this connection between text reference and subject. These tags are combined to create a general database of subjects of ancient texts. The database is thus based on existing expert-made indices, unified and assisted by digital means.
<br>The results for each search are divided into three: <b>highly validated</b> results, where the reference is tagged with the subject in more than one book; <b> validated</b> results, where the reference is tagged with the subject only in one book, but more than once; and <b> non-validated</b> results, where the reference is tagged with the subject only once, in one book.
<br>The database includes general subjects, ideas, names and places, almost all in English; the subjects are the same you would find in a good subject index of a book.<br>
<br>The site attempts to provide full-text (in source language and English) for highly validated results. Full texts for Hebrew Bible and rabbinic texts is kindly supplied by <a href="https://www.sefaria.org">Sefaria</a>; for Greek and Latin texts, by <a href="https://scaife.perseus.org">Perseus Scaife</a>, for the Quran, by Tanzil.net.
<br>The site is part of a digital humanities research project investigating innovative methods for text topic retrieval, conducted by <a href="https://haifa.academia.edu/MosheBlidstein">Moshe Blidstein</a> of the General History Department and the Haifa Center for Mediterranean History and <a href="http://lecturers.haifa.ac.il/en/management/draban">Daphne Raban</a>, the Department of Information & Knowledge Management, both at the University of Haifa.
<br>For information and suggestions, please contact mblidstei@univ.haifa.ac.il. <br>


</div>
    </form>'''


@app.route('/', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
  if request.method == 'POST':  #this block is only entered when the form is submitted
    texts_subjects = pd.read_csv("/home/moblid/mysite/texts_subjects1.csv", encoding='utf8')

    yyy = ""
    vv = []
    vv1 = []
    vv1 = pd.DataFrame({"a":vv1})
    lengthvv1 = 0
    vv = pd.DataFrame({"a":vv})


    def hyphenate(x):#this takes numbers as they are usually printed(e.g., 1-4, 35-7, 109-11) and expands them (e.g., 1, 2, 3, 4, 35, 36, 37, 109, 110, 111)
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
    						new = a[0:-(len(b))]+b[-(len(b)):]
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

    def hyph(reflist):
      if "," in reflist:
        try:
          ranges = []
          reflist = reflist.replace(" ", "")
          reflist = [int(k) for k in reflist.split(',')]
          for k,g in groupby(enumerate(reflist),lambda x:x[0]-x[1]):
            group = (map(itemgetter(1),g))
            group = list(map(int,group))
            ranges.append((group[0],group[-1]))
          tt = repr(','.join(['%d' % s if s == e else '%d-%d' % (s, e) for (s, e) in ranges]))
          tt = tt.replace(",", ", ")
          strtt=tt.strip('[]')
          strtt = strtt.replace("'", "")
          return(strtt)
        except:
          reflist = reflist.replace(",", ", ")
          return(reflist)
      else:
        reflist = reflist.replace(",", ", ")
        return(reflist)

    def natural(refs1):
      refs1 = str(refs1)
      refs1 = refs1.replace(" ", "")
      listb = refs1.split(",")
      listb = list(set(listb))
      try:
        listb = natsorted(listb)
        listb =", ".join(listb)
        return(listb)
      except:
        listb = natsorted(listb)
        listb =", ".join(listb)
        return(listb)

    def sortref(refs1):
      refs1 = str(refs1)
      refs1 = refs1.replace(" ", "")
      listb = refs1.split(",")
      listb = list(set(listb))
      try:
        listb = sorted(listb)
        listb =", ".join(listb)
        return(listb)
      except:
        return(listb)

    def dup(refs1):
      refs1 = str(refs1)
      refs1 = refs1.replace("# ", "#")
      refs1 = refs1.replace(" # ", "#")
      listb = refs1.split("#")
      listb = list(set(listb))

      try:
        listb = sorted(listb)
        listb =", ".join(listb)
        #listb = listb.replace("\$", "; ")
        return(listb)
      except:
        return(listb)
        #listb = listb.replace("\$", "; ")

    def rehyph(refs3):
        refs3 = str(refs3)
        zar=[]
        if "," in refs3:
            if not "." in refs3:
                x = hyph(refs3)
                return(x)
            elif bool(re.search('[a-zA-Z]', refs3)):
                return(refs3)
            else:
                try:
                    refs3 = refs3.replace(" ", "")
                    listb = refs3.split(",")
                    ii = pd.DataFrame({"0":listb})
                    ii[["0", "1"]] = ii["0"].str.rsplit(".", n = 1, expand = True)
                    ii["1"] = ii["1"].astype(int)
                    ii= ii.sort_values(by=["0","1"])
                    ii["1"] = ii["1"].astype(str)
                    mm0 = ii.groupby(["0"])["1"].apply(lambda x: ', '.join(x)).reset_index()
                    mm0 = mm0.sort_values(by=["0","1"])
                    mm0["0"] = mm0["0"].astype(str)
                    mm0["1"] = mm0["1"].apply(hyph)
                    mm0["1"] = mm0["1"].str.replace("'", "")
                    #mm0["1"] = mm0["1"].str.replace("-","-"+mm0["0"]+".")
                    mm0["2"] = mm0["0"]+"."+mm0["1"]
                    zar = mm0["2"].values.tolist()
                    zar = [str(i) for i in zar]
                    zar = [re.sub(" ","",i) for i in zar]
                    zar = [re.sub(",",", "+str(k.rsplit('.',1)[0])+".",k) for k in zar]
                    zar = [re.sub("-","-"+str(k.split('.',1)[0])+".",k) for k in zar]
                    strlonglist = ', '.join(zar)
                    return(strlonglist)
                except:
                    return(refs3)
        else:
            return(refs3)
            #return('err')

    def bookname(bookwithnum):
      try:
        bookpd["book bibliographic info"] = bookpd["book bibliographic info"].astype(str)
        bookmerge = pd.merge(bookwithnum, bookpd, on=["book bibliographic info"], how="left")
        bookmerge = bookmerge[["author","work","ref", "subject","titleref", 'page']]
        bookmerge.columns = [["author","work","ref", "subject","book", 'page']]
        return(bookmerge)
      except:
        return(bookwithnum)

    def urn(unlinkeddata):#create links to texts online, using the file urns.csv
      try:
        #urnpd = pd.read_csv(urndata)
        urnmerge = pd.merge(unlinkeddata, urnpd, on=["author","work"], how="left")
        urnmerge['ref'] = urnmerge['ref'].astype(str)
        if option=="and":
          urnmerge = urnmerge[["author","work","ref","reflink","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2"]]
        else:
          urnmerge = urnmerge[["author","work","ref", "reflink", "subject",'book bibliographic info', 'page']]
        listreflink = []
        for a in range (len(urnmerge.index)):
          refb = str(urnmerge.iloc[a, 2])
          linkrefb = str(urnmerge.iloc[a, 3])
          if "http" in linkrefb:
            if "," in refb:
              refb = refb.replace(" ", "")
              listrefb = refb.split(",")
              listreflink = []
              for x in range(0, len(listrefb)):
                linkrefb = str(urnmerge.iloc[a, 3])
                hub = str((listrefb[x]))
                linkrefc = linkrefb.replace("linkref", hub)
                listreflink.append(linkrefc)
            else:
              linkrefc = linkrefb.replace("linkref", refb)
              listreflink.append(linkrefc)
            strreflink = str(listreflink)
            strreflink = strreflink.replace(",",", ")
            strreflink = strreflink.replace("'","")
            strreflink=strreflink.strip('[]')
            urnmerge.iloc[a, 2] = strreflink
            listreflink = []
        linkeddata = urnmerge
        linkeddata.drop(["reflink"], axis=1, inplace=True)
        return(linkeddata)
      except:
        empty = "Sorry, there are no matches in the database. Please try again with a different search term or with less filters"
        return(unlinkeddata)

    def splitchap (x):
      x = str(x)
      y = x.split('.')[0]
      return y

    def valid_rep(df):
    	dfz = df
    	dfz["refi"] = dfz["ref"].str.replace("/.","@",1)
    	dfz["refx"] = dfz["refi"].str.partition('.')[2]
    	dfz["refv"] = dfz["refi"].str.partition('.')[0]
    	dfz = dfz.replace(r'^\s*$', "xx", regex=True)
    	dfz = dfz.sort_values(by=["author","work","refv","refx"],ascending=False)
    	dfz["joined"] = dfz["work"].map(str) + " " + dfz["refv"]
    	dfz2 = dfz
    	dfz = dfz.astype(str).groupby('joined').agg({'refx':','.join,'page':'#'.join, 'book bibliographic info':'#'.join, 'ref':'#'.join, 'work':'first','author':'first','subject':'#'.join}).reset_index()
    	dfz1 = dfz[dfz["subject"].str.contains("#")]
    	dfz1 = dfz1[["joined"]]
    	dfc = pd.merge(dfz1,dfz2, on="joined", how="left")
    	dfq = df[["author","work","ref","book bibliographic info","page","subject"]]
    	dfq = dfq[dfq["ref"].str.split(".").str.len()<3]
    	dfq["refx"] = dfq["ref"].str.partition('.')[2]
    	dfq["refv"] = dfq["ref"].str.partition('.')[0]
    	dfq = dfq.replace(r'^\s*$', "xx", regex=True)
    	dfq["joined"] = dfq["work"].map(str) + " " + dfq["refv"]
    	dfq2 = dfq
    	dfq = dfq.sort_values(by=["author","work","refv","refx"],ascending=False)
    	dfq = dfq.astype(str).groupby('joined').agg({'refx':','.join,'page':'#'.join, 'book bibliographic info':'#'.join, 'ref':'#'.join, 'work':'first','author':'first','subject':'#'.join}).reset_index()
    	dfq1 = dfq[dfq["subject"].str.contains("#")&dfq["refx"].str.contains("xx")]
    	dfq1 = dfq1[["joined"]]
    	dfd = pd.merge(dfq1,dfq2, on="joined", how="left")
    	dfc = pd.concat([dfc,dfd])
    	dfc = dfc.drop_duplicates(subset = ["author","work","ref"], keep='last')
    	dfc = dfc.sort_values(by=["author","work","refv","refx"],ascending=False)
    	dfc["j"] = dfc["author"]+"$"+dfc["work"]+"$"+dfc["book bibliographic info"]+"$"+dfc["page"]+"$"+dfc["subject"]
    	dfc["a"] = np.where(dfc['refx']=="xx", dfc['j'],np.nan)
    	dfc = dfc.drop(["j"], axis=1)
    	dfc.rename(columns={"a":"j"}, inplace=True)
    	dfc = dfc[["ref","j","refx"]]
    	dfc = dfc.fillna(method="ffill")
    	dfc['author'], dfc['work'], dfc['book bibliographic info'], dfc['page'], dfc['subject'] = dfc['j'].str.split('$').str
    	dfc = dfc[dfc["refx"]!="xx"]
    	dfc = dfc.drop(["j"], axis=1)
    	dfc = dfc[["author","work","ref","book bibliographic info","page","subject"]]
    	df = df[["author","work","ref","book bibliographic info","page","subject"]]
    	g = pd.concat([df,dfc])
    	g = g.sort_values(by=["author","work","ref"],ascending=False)
    	return(g)

    if "step" not in request.form:

      empty = ""
      synonyms = []
      c = request.form.get('c')
      d = request.form.get('d')
      option = request.form.get('option')
      email = request.form.get('email')
      now = str(datetime.now())
      searchford = []
      lengthvv=0
      d_texts_subjects = 1
      d_subjects = []


      fd = open("/home/moblid/mysite/emails.csv", "a")
      fd.write(email)
      fd.write(",".join([now, c, d]))
      fd.write("\n")
      fd.close()
      pd.set_option('display.max_colwidth', -1)


      if c=="":
          randrow = random.randint(0,2000)
          texts_subjects["number of references in database"] = \
                texts_subjects["C"].str.len()
          texts_subjects = texts_subjects\
            [["subject","number of references in database"]]
          subjects_count = texts_subjects.sort_values(by=["number of references in database"],ascending=False)
          subjects_count = subjects_count.head(2000)
          c = subjects_count.iloc[randrow,0]
      db=MySQLdb.connect(
        host=\
                'moblid.mysql.pythonanywhere-services.com',
        user='moblid',
        passwd='s4MYP9KSyYkZ6B6',
        db='moblid$default',
        charset='utf8' )
      dds = []
      if c:
        c2 = "'%"+c+"%'"
        sql_for_df_sub = "SELECT * FROM texts_subjects WHERE subject like "+c2
        texts_subjects1 = pd.read_sql_query(sql_for_df_sub , db)
        texts_subjects2 = texts_subjects1[texts_subjects1["subject"].str.contains('\\b'+c+'\\b', case=False, na=False)]
        texts_subjects3 = texts_subjects1[texts_subjects1["subject"].str.contains('\\b'+c+'s\\b', case=False, na=False)]
        texts_subjects1 = pd.concat([texts_subjects2,texts_subjects3])
        subjects = texts_subjects1['subject'].values.tolist()
        texts_subjects1["C"] = texts_subjects1["C"].apply(hyphenate)
        cs = texts_subjects1['C'].values.tolist()
        ccs = [item for sublist in cs for item in sublist]
        lccs = len(ccs)
        pd.set_option('display.max_colwidth', -1)
        if option=="and":
          d2 = "'%"+d+"%'"
          sql_for_df_sub_d = "SELECT * FROM texts_subjects WHERE subject like "+d2
          d_texts_subjects = pd.read_sql_query(sql_for_df_sub_d , db)
          d_subjects = d_texts_subjects['subject'].values.tolist()
          d_texts_subjects["C"] = d_texts_subjects["C"].apply(hyphenate)
          ds = d_texts_subjects['C'].values.tolist()
          dds = [item for sublist in ds for item in sublist]


      return render_template('index.html', subjects = subjects, step="choose_lower", c=c, lccs = lccs,\
      ccs =ccs, dds = dds, d = d, option = option, d_texts_subjects = d_texts_subjects, d_subjects = d_subjects)

    elif request.form["step"] == "choose_upper":
      titles = pd.read_csv("/home/moblid/mysite/titlesa.csv", encoding='utf-8')
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
      lengthvv = 0
      l = len(k)

    #   artart =[]
    #   c_subject_art = c_subject
    #   try:
    #     if "," in c_subject_art:
    #       c_subject_art = c_subject_art.split(",")[0]
    #     c_art = "https://collectionapi.metmuseum.org/public/collection/v1/search?dateBegin=-800&dateEnd=800&q="+c_subject_art
    #     art1 = requests.get(c_art)
    #     art = art1.text
    #     art = art.split("objectIDs\":[")[1]
    #     art = art.split("]}")[0]
    #     art = art.replace("\'", "")
    #     art = art.split(",")
    #     art = art[0:10]
    #     for a in range(len(art)):
    #       art_a = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/objects/"+art[a])
    #       art_a = art_a.text
    #       art_l = art_a.split("primaryImageSmall\":\"")[1]
    #       art_l = art_l.split("jpg")[0]
    #       art_k = art_a.split("objectName\":\"")[1]
    #       art_k = art_k.split("\",\"")[0]
    #       art_t = art_a.split("title\":\"")[1]
    #       art_t = art_t.split("\",\"")[0]
    #       artart.append("<img src=\""+art_l+"jpg\" height=\"200\"></img>")
    #       artart.append(art_k)
    #       artart.append(art_t)
    #   except:
    #     artart=["empty"]
    #   wikiart = pd.read_csv("/home/moblid/mysite/wikidata2.csv", encoding='utf-8')
    #   wikiart = wikiart[["image","depictsLabel"]]
    #   wikiart["depictsLabel"] = wikiart["depictsLabel"].str.lower()
    #   wikiart = wikiart[wikiart["depictsLabel"].str.contains(c_subject_art, na=False)]
    #   wikiart["image"] = wikiart["image"].astype(str)
    #   wikiart_list = wikiart["image"].values.tolist()
    #   wikiart_list = list(set(wikiart_list))
    #   wikiart_list = ["<img src=\"" + s + "?width=300px\" height=\"200\"></img>" for s in wikiart_list]
    #   artart.extend(wikiart_list)
    #   mc = pd.read_csv("/home/moblid/mysite/mc2.csv", encoding='utf-8')
    #   mc["descriptiona"] = mc["description"].str.lower()
    #   mc = mc[mc["descriptiona"].str.contains(c_subject_art, na=False)]
    #   mc = mc.drop_duplicates(keep = "first")
    #   mc_list = mc["image"].values.tolist()
    #   mc_list_desc = mc["description"].values.tolist()
    #   mc_list = ["<img src=\"" + s + "?width=300px\" height=\"200\"></img>" for s in mc_list]
    #   res = []
    #   for a,b in zip(mc_list, mc_list_desc):
    #     res += [a,b]
    #   artart.extend(res)


      if fulltext!="f":
        full = "fulltext"
      else:
        full = "not full"
      fd = open("/home/moblid/mysite/emails.csv", "a")
      fd.write(",".join([full, author, work, ref, lang, cs, ce, option, c_subject,str(len(ccs))]))
      fd.write("\n")
      fd.close()
      pd.set_option('display.max_colwidth', -1)
      df = []
      df = pd.DataFrame({"a":df})
      df1 = []
      df1 = pd.DataFrame({"subject":df1,"ref":df1,"page":df1,"book bibliographic info":df1,"number":df1,"C":df1})
      ccs = ",".join(ccs)
      ccs = ccs.replace("[","")
      ccs = ccs.replace("]","")
      ccs = ccs.split(", ")
      ccs1 = tuple(ccs)
      db=MySQLdb.connect(
        host='moblid.mysql.pythonanywhere-services.com',
        user='moblid',
        passwd='s4MYP9KSyYkZ6B6',
        db='moblid$default',
        charset='utf8' )
      sql_for_df = "SELECT * FROM textsa WHERE C IN {}".format(ccs1)
      now1 = str(datetime.now())
      c2 = "'%"+c_subject+"%'"
      textsa = pd.read_sql_query(sql_for_df , db)
      if add_key:
        textsa=textsa[textsa['subject'].str.contains(add_key)]
      if no_key:
        textsa=textsa[~textsa['subject'].str.contains(no_key)]
      now2 = str(datetime.now())
      textsa=textsa[textsa['subject'].isin(k)]
      textsa['number'] = textsa['number'].astype(str)
      textsa['number'] = textsa['number'].str.replace('\\.0', '')
      titles['number'] = titles['number'].astype(str)
      titles['number'] = titles['number'].str.replace('\\.0', '')
      now3 = str(datetime.now())
      titles["title1"] = titles["title1"].str.title()
      titles["author1"] = titles["author1"].str.title()
      textsb = pd.merge(textsa, titles, on="number", how="left")
      textsb.rename(columns={"title1": "work"}, inplace=True)
      textsb.rename(columns={"author1": "author"}, inplace=True)
      subjects = textsb[["author","book bibliographic info","centend","centstart","language","page","ref","subject","work"]]
      kk = subjects
      kk["ref"] = kk["ref"].str.replace("DK","")
      kk["ref"] = kk["ref"].str.replace("Fr\.","")
      kk["ref"] = kk["ref"].str.lower()
      kk["ref"] = kk["ref"].str.strip()
      kk["ref"] = kk["ref"].str.replace("\. ",".")
      now4 = str(datetime.now())
      if len(kk.index)!=0:
        kk = kk[~kk.applymap(lambda x: len(str(x)) > 90).any(axis=1)]
      else:
        empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"
      lengthkk = len(kk.ref)

      kk['book bibliographic info'] = kk['book bibliographic info'].astype(str)
      bb = kk.loc[:, "subject"]
      bb1 = bb.drop_duplicates(keep = "first")
      Listkk = bb1.tolist()
      lengthkk = len(kk.ref)
      if cs != "any":
        cs = int(cs)
        kk = kk.loc[kk['centend'] != "Nan"]
        kk[['centend']] = kk[['centend']].apply(pd.to_numeric)
        kk = kk[kk.centend >= cs]
      if ce != "any":
        ce = int(ce)
        kk = kk.loc[kk['centstart'] != "Nan"]
        kk[['centstart']] = kk[['centstart']].apply(pd.to_numeric)
        kk = kk[kk.centstart <= ce]
      if lang!= "all":
        kk = kk[kk["language"].str.contains(lang, na=False)]
      if author:
        kk = kk[kk["author"].str.contains(author, na=False)]
      if work:
        kk = kk[kk["work"].str.contains(work, na=False)]
      if ref:
        if "." in ref:
          kk = kk[kk.ref == ref]
        if "." not in ref:
          kk["refchap"] = kk["ref"].apply(splitchap)
          kk = kk[kk.refchap == ref]
      if option=="and":
        dfd = []
        dfd = pd.DataFrame({"a":dfd})
        dfd1 = []
        dfd1 = pd.DataFrame({"subject":dfd1,"ref":dfd1,"page":dfd1,"book bibliographic info":dfd1,"number":dfd1,"C":dfd1})
        dds = ",".join(dds)
        dds = dds.replace("[","")
        dds = dds.replace("]","")
        dds = dds.split(", ")
        dds1 = tuple(dds)
        db=MySQLdb.connect(
        host='moblid.mysql.pythonanywhere-services.com',
        user='moblid',
        passwd='s4MYP9KSyYkZ6B6',
        db='moblid$default',
        charset='utf8' )
        sql_for_dfd = "SELECT * FROM textsa WHERE C IN {}".format(dds1)
        textsad = pd.read_sql_query(sql_for_dfd , db)
        kk1 = kk
        textsa = textsad[["book bibliographic info","page","ref","subject","number"]]
        textsa['number'] = textsa['number'].astype(str)
        textsa['number'] = textsa['number'].str.replace('\\.0', '')
        textsa['ref'] = textsa['ref'].str.replace('\. ', '.')
        titles['number'] = titles['number'].astype(str)
        titles['number'] = titles['number'].str.replace('\\.0', '')
        textsb = pd.merge(textsa, titles, on="number", how="left")
        textsb.rename(columns={"title1": "work"}, inplace=True)
        textsb.rename(columns={"author1": "author"}, inplace=True)
        subjectsd = textsb[["author","book bibliographic info","centend","centstart","language","page","ref","subject","work"]]
        kk2 = subjectsd
        kk1["ref"] = kk1["ref"].astype(str)
        kk2["ref"] = kk2["ref"].astype(str)
        kk1["results"] = kk1["work"].map(str) + " " + kk1["ref"]
        kk2["results"] = kk2["work"].map(str) + " " + kk2["ref"]
        kk = kk1.merge(kk2, on="results", how="inner")
        bb3 = kk.loc[:, "subject_y"]
        bb4 = bb3.drop_duplicates(keep = "first")
        Listbb3 = bb4.tolist()
        if 1 == 0:
        #if len(kk) == 0:
          #kk = subjects[subjects["subject"].str.contains('|'.join(synonyms), na=False)]
          yyy = "There were no references Tagged with both subjects, please search with one only"
          #if len(kk.index) == 0:
          #  kk = subjects[subjects["subject"].str.contains('|'.join(searchford))]
          #  yyy = "There were no references Tagged with both subjects, so a search was performed with the second only"
          #bb = kk.loc[:, "subject"]
          #bb1 = bb.drop_duplicates(keep = "first")
          #Listkk = bb1.tolist()
          #kk = kk.drop(['book bibliographic info', 'page'], axis=1)
          #kk = kk[["author", "work", "ref", "subject"]]
          #lengthkk = len(kk.ref)
        else:
          kk['page_y'] = kk['page_y'].astype(str)
          kk['page_x'] = kk['page_x'].astype(str)
          kk = kk.drop(["ref_y", "work_y", "author_y", "results"], axis=1)
          kk['ref_x'] = kk['ref_x'].astype(str)
          bb = kk.loc[:, "subject_x"]
          bb1 = bb.drop_duplicates(keep = "first")
          Listkk = bb1.tolist()

          kk.rename(columns={"author_x": "author"}, inplace=True)
          kk.rename(columns={"work_x": "work"}, inplace=True)
          kk.rename(columns={"subject_x": "subject 1"}, inplace=True)
          kk.rename(columns={"subject_y": "subject 2"}, inplace=True)
          kk.rename(columns={"book bibliographic info_x": "book 1 info"}, inplace=True)
          kk.rename(columns={"book bibliographic info_y": "book 2 info"}, inplace=True)
          kk.rename(columns={"page_x": "page 1"}, inplace=True)
          kk.rename(columns={"page_y": "page 2"}, inplace=True)
          kk.rename(columns={"ref_x": "ref"}, inplace=True)
          kk = kk.astype(str).groupby('work').agg({'subject 1':'; '.join, 'subject 2':'; '.join, 'page 1':','.join, 'page 2':','.join, 'ref':','.join, 'author':'first', 'book 1 info':'first','book 2 info':'first',}).reset_index()

          kk = kk.groupby(["author","work","subject 1","book 1 info","page 1","book 2 info","page 2","ref"])["subject 2"].apply(lambda x: '; '.join(x)).reset_index()
          kk = kk.groupby(["work","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2","ref"])["author"].apply(lambda x: ', '.join(x)).reset_index()
          kk = kk.groupby(["author","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2","ref"])["work"].apply(lambda x: ', '.join(x)).reset_index()

          kk = kk.groupby(["author","work","subject 1","subject 2","page 1","book 2 info","page 2","ref"])["book 1 info"].apply(lambda x: ', '.join(x)).reset_index()
          kk = kk.groupby(["author","work","subject 1","subject 2","book 1 info","book 2 info","page 2","ref"])["page 1"].apply(lambda x: ', '.join(x)).reset_index()
          kk = kk.groupby(["author","work","subject 1","subject 2","book 1 info","book 2 info","page 1","ref"])["page 2"].apply(lambda x: ', '.join(x)).reset_index()
          kk = kk.groupby(["author","work","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2"])["ref"].apply(lambda x: ', '.join(x)).reset_index()

          kk = kk.groupby(["author","work","subject 1","subject 2","page 1","book 2 info","page 2","ref"])["book 1 info"].apply(lambda x: ', '.join(x)).reset_index()

          kk = kk[["author","work","ref","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2"]]


          kk["ref"] = kk["ref"].apply(natural)
          kk["ref"] = kk["ref"].apply(rehyph)
          kk["page 1"] = kk["page 1"].str.replace('\\.0', '')
          kk["page 2"] = kk["page 2"].str.replace('\\.0', '')
          kk["book 1 info"] = kk["book 1 info"].str.replace('\\.0', '')
          kk["book 2 info"] = kk["book 2 info"].str.replace('\\.0', '')
          kk["page 1"] = kk["page 1"].apply(sortref)
          kk["page 2"] = kk["page 2"].apply(sortref)
          kk["page 1"] = kk["page 1"].apply(hyph)
          kk["page 2"] = kk["page 2"].apply(hyph)
          kk['subject 1'] = kk['subject 1'].str.split().apply(lambda x: OrderedDict.fromkeys(x).keys()).str.join(', ')
          kk['subject 2'] = kk['subject 2'].str.split().apply(lambda x: OrderedDict.fromkeys(x).keys()).str.join(', ')
          kk['subject 1'] = kk['subject 1'].str.replace(', ', ' ')
          kk['subject 2'] = kk['subject 2'].str.replace(', ', ' ')

          kk = kk[["author","work","ref","subject 1","subject 2","book 1 info","page 1","book 2 info","page 2"]]
          kk['book 1 info'] = kk['book 1 info'].map(bookdict)
          kk['book 2 info'] = kk['book 2 info'].astype(str)
          kk['book 2 info'] = kk['book 2 info'].map(bookdict)

          lengthkk = len(kk.ref)
          #kk = urn(kk)
          #synonyms = synonyms +searchford
          Listkk = Listkk+Listbb3
      if option!="and":
        now5 = str(datetime.now())
        bb = kk.loc[:, "subject"]
        bb1 = bb.drop_duplicates(keep = "first")
        Listkk = bb1.tolist()
        kk = kk.sort_values(by=["author", "work", "ref"])
        kk['page'] = kk['page'].astype(str)
        kk['page'] = kk['page'].str.replace('\\.0', '')
        kk['book bibliographic info'] = kk['book bibliographic info'].str.replace('\\.0', '')
        kk = pd.merge(kk,bookpd, on=['book bibliographic info'], how="left")
        kk['book bibliographic info'] = kk['titleref']
        kk = kk.drop(["titleref"], axis=1)
        kk['page'] = "<a href=https://books.google.co.il/books?id="+kk['gcode']+"&lpg=PP1&pg=PA"+kk['page']+"#v=onepage&q&f=false>"+kk['page']+"</a>"
        kk = kk.drop(["gcode"], axis=1)
        kk['ref'] = kk['ref'].astype(str)
        kk['ref'] = kk['ref'].str.replace('\s', '.')
        kk = kk[~kk["ref"].str.contains("00:00:00", na=False)]
        #kk_z = valid_rep(kk)
        #vv = kk_z
        vv = kk
        #kk.to_csv("/home/moblid/mysite/try.csv")
        vv = vv.drop_duplicates(keep = "first")
        vv["joined"] = vv["work"].map(str) + vv["ref"]
        #vvch0 = vv
        vv = vv.astype(str).groupby('joined').agg({'page':','.join, 'book bibliographic info':'#'.join, 'ref':','.join, 'work':'first','author':'first','subject':'#'.join}).reset_index()
        #vvch1 = vv
        vv['book bibliographic info'] = vv['book bibliographic info'].astype(str)
        vv = vv[vv['book bibliographic info'].str.contains('#', na=False)]
        #vv["page"] = vv["page"].apply(dup)
        vv["subject"] = vv["subject"].apply(dup)
        vv['book bibliographic info'] = vv["book bibliographic info"].apply(dup)
        vv = vv.drop(['joined'], axis=1)
        now6 = str(datetime.now())
        if len(vv)!=0:
          vv["joined"] = vv["work"].map(str) + " " + vv["subject"]
          vv = vv.astype(str).groupby('joined').agg({'ref':','.join, 'work':'first','author':'first','subject':'#'.join, 'book bibliographic info':'#'.join, 'page':'first'}).reset_index()
          vv["subject"] = vv["subject"].apply(dup)
          vv['book bibliographic info'] = vv["book bibliographic info"].apply(dup)
          vv = vv.drop(['joined'], axis=1)
          vv = vv.sort_values(by=["work", "ref"])
          vv = vv[["author", "work", "ref", "subject",'book bibliographic info', 'page']]
          vv = vv.drop_duplicates(keep = "first")
          lengthvv = len(vv.ref)
          vv["ref"] = vv["ref"].apply(natural)
          vv["ref"] = vv["ref"].apply(rehyph)
          vv = vv.sort_values(by=["author", "work", "ref"])
          vv = vv.reset_index(drop=True)
          vv1 = vv[vv['book bibliographic info'].str.contains(',', na=False)]
          if len(vv1)!=0:
            vv1 = vv1.sort_values(by=["author", "work", "ref"])
            lengthvv1 = len(vv1.ref)
            vv1 = vv1.reset_index(drop=True)
        if len(kk.index)!=0:
            #kk = kk.groupby(["author", "work", "subject",'book bibliographic info', 'ref','refcite'])['page'].apply(lambda x: ', '.join(x)).reset_index()
            #kk = kk.groupby(["author", "work", "subject",'book bibliographic info', 'page','refcite'])['ref'].apply(lambda x: ', '.join(x)).reset_index()
            #kk = kk.groupby(["author", "work", "ref", 'book bibliographic info', 'page','refcite'])['subject'].apply(lambda x: ', '.join(x)).reset_index()
            #kk = kk.groupby(["author", "work", "ref", 'page', 'subject','refcite'])['book bibliographic info'].apply(lambda x: ', '.join(x)).reset_index()
            #kk = kk.groupby(["author", "work", "ref", 'page', 'subject','book bibliographic info'])['refcite'].apply(lambda x: ', '.join(x)).reset_index()
            #kk = kk.sort_values(by=["work", "ref"])
            #kk = kk[["author", "work", "ref", "subject",'book bibliographic info', 'page','refcite']]
          kk = kk.groupby(["author", "work", "subject",'book bibliographic info', 'page'])['ref'].apply(lambda x: ', '.join(x)).reset_index()
          kk = kk.groupby(["author", "work", "ref", 'book bibliographic info', 'page'])['subject'].apply(lambda x: ', '.join(x)).reset_index()
          kk = kk.groupby(["author", "work", "ref", 'page', 'subject'])['book bibliographic info'].apply(lambda x: ', '.join(x)).reset_index()
          kk = kk.sort_values(by=["work", "ref"])
          kk = kk[["author", "work", "ref", "subject",'book bibliographic info', 'page']]
          lengthkk = len(kk.ref)
          now7 = str(datetime.now())
        else:
          empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"
      try:
        kk = kk.sort_values(by=["author", "work","ref"])
        lengthkk = len(kk.ref)
      except:
        empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"
      if len(kk.index)==0:
        empty = "Sorry, there are no matches in the database. Please try with a different search term or with less filters"

      else:
        now8 = str(datetime.now())
        kk["ref"] = kk["ref"].apply(natural)
        now9 = str(datetime.now())
        kk["ref"] = kk["ref"].apply(rehyph)
        if option!="and":
          kk = kk.groupby(["author", "work", "subject",'book bibliographic info', 'ref'])['page'].apply(lambda x: ', '.join(x)).reset_index()
          kk["page"] = kk["page"].apply(hyph)
          kk = kk[["author", "work", "ref", "subject",'book bibliographic info', 'page']]
        kk = kk.drop_duplicates(keep = "first")
        if fulltext != "f":
          if (len(kk)<100) and (len(kk!=0)):
            kk = crn(kk)
            kk = crneng(kk)
            #kk["refcite"] = kk["refcite"]
            #kk["refengcite"] = kk["refengcite"]
            if  option!="and":
              kk["results"] = kk["author"]+", <i>"+kk["work"]+"</i>, "+kk["ref"]+"<br><br>    Tagged with subjects: "+kk["subject"]+"<br><br>    Found in books: "+kk["book bibliographic info"]+" on pages: "+kk["page"]+"<table><tr><td style='min-width:600px'>"+kk["refcite"]+"</td><td>"+kk["refengcite"]+"</td></tr></table>"
              kk = kk[['results']]
            if  option=="and":
              kk["results"] = kk["author"]+", <i>"+kk["work"]+"</i>, "+kk["ref"]+"<br><br>    Tagged with subjects: "+kk["subject 1"]+"<br>"+kk["subject 2"]+"<br><br>"
              kk["book 1"] = kk["book 1 info"]+", "+kk["page 1"]
              kk["book 2"] = kk["book 2 info"]+", "+kk["page 2"]
              kk = kk[['results','refcite','refengcite','book 1','book 2']]
            kk.rename(columns={"refcite": "full text.............................................................................."}, inplace=True)
            kk.rename(columns={"refengcite": "English translation.............................................................................."}, inplace=True)
          if len(vv)!=0:
            vv = crn(vv)
            vv = crneng(vv)
            #vv["refcite"] = vv["refcite"]
            #vv["refengcite"] = vv["refengcite"]
            if  option!="and":
              vv["results"] = vv["author"]+", <i>"+vv["work"]+"</i>, "+vv["ref"]+"<span style='padding-left: 20px; display:block'><br>&nbsp;&nbsp;&nbsp;Tagged with subjects: "+vv["subject"]+"<br><br>&nbsp;&nbsp;Found in books: "+vv["book bibliographic info"]+", pages: "+vv["page"]+"</span><table><tr><td style='min-width:600px'>"+vv["refcite"]+"</td><td>"+vv["refengcite"]+"</td></tr></table>"
              vv = vv[['results']]
            if  option=="and":
              vv["results"] = vv["author"]+", <i>"+vv["work"]+"</i>, "+vv["ref"]+"<br><br>    Tagged with subjects: "+vv["subject 1"]+"<br>"+vv["subject 2"]+"<br><br>"
              vv["book 1"] = vv["book 1 info"]+", "+vv["page 1"]
              vv["book 2"] = vv["book 2 info"]+", "+vv["page 2"]
              vv = vv[['results','refcite','refengcite','book 1','book 2']]
            vv.rename(columns={"refcite": "full text.............................................................................."}, inplace=True)
            vv.rename(columns={"refengcite": "English translation.............................................................................."}, inplace=True)
          if len(vv1)!=0:
            vv1 = crn(vv1)
            vv1 = crneng(vv1)
            vv1["refcite"] = vv1["refcite"]
            vv1["refengcite"] = vv1["refengcite"]
            if  option!="and":
              vv1["Index1"] =vv1.index
              vv1["Index1"]=vv1["Index1"]+1
              vv1["results"] = vv1["Index1"].astype(str)+". "+vv1["author"]+", <i>"+vv1["work"]+"</i>, "+vv1["ref"]+"<span style='padding-left: 20px; display:block'><br>Tagged with subjects: "+vv1["subject"]+"<br><br>    Found in books: "+vv1["book bibliographic info"]+", pages: "+vv1["page"]+"</span>"
              vv1 = vv1[['results','refcite','refengcite']]
            if  option=="and":
              vv1["results"] = vv1["author"]+", <i>"+vv1["work"]+"</i>, "+vv1["ref"]+"<br><br>    Tagged with subjects: "+vv1["subject 1"]+"<br>"+vv1["subject 2"]+"<br><br>"
              vv1["book 1"] = vv1["book 1 info"]+", "+vv1["page 1"]
              vv1["book 2"] = vv1["book 2 info"]+", "+vv1["page 2"]
              vv1 = vv1[['results','refcite','refengcite','book 1','book 2']]
            vv1.rename(columns={"refcite": "full text.............................................................................."}, inplace=True)
            vv1.rename(columns={"refengcite": "English translation.............................................................................."}, inplace=True)

        else:
          if option!="and":
            kk["results"] = "<b>"+kk["author"]+", <i>"+kk["work"]+"</i>, "+kk["ref"]+"</b><span style='padding-left: 50px; display:block'><br>&nbsp;&nbsp;&nbsp;Tagged with subjects: "+kk["subject"]+"<br><br>    &nbsp;&nbsp;&nbsp;Found in books: "+kk["book bibliographic info"]+", pages: "+kk["page"]+"</span>"
            kk = kk[['results']]
            if len(vv)!=0:
              vv["Index1"] =vv.index
              vv["Index1"]=vv["Index1"]+1
              vv["results"] = "<b>&emsp;"+vv["Index1"].astype(str)+". "+vv["author"]+", <i>"+vv["work"]+"</i>, "+vv["ref"]+"</b><span style='padding-left: 50px; display:block'><br>&emsp;Tagged with subjects: "+vv["subject"]+"<br><br>    &emsp;Found in books: "+vv["book bibliographic info"]+", pages: "+vv["page"]+"</span>"
              vv = vv[['results']]
            if len(vv1)!=0:
              now10 = str(datetime.now())
              if len(vv1)<80:
                vv1 = crn(vv1)
                vv1 = crneng(vv1)
                vv1["Index1"] =vv1.index
                vv1["Index1"]=vv1["Index1"]+1
                try:
                  vv1["results"] = "<b>&emsp;"+vv1["Index1"].astype(str)+". "+vv1["author"]+", <i>"+vv1["work"]+"</i>, "+vv1["ref"]+"</b><span style='padding-left: 50px; display:block'><br>&emsp;Tagged with subjects: "+vv1["subject"]+"<br><br>&emsp;Found in books: "+vv1["book bibliographic info"]+", pages: "+vv1["page"]+"</span><br><br><table style='font-family:Palatino;background-color:white;'><tr style='font-family:Palatino;background-color:white;'><td style='min-width:600px;font-family:Palatino;background-color:white;'>"+vv1["refcite"]+"</td><td>"+vv1["refengcite"]+"</td></tr></table>"
                except:
                  vv1["results"] = "<b>&emsp;"+vv1["Index1"].astype(str)+". "+vv1["author"]+", <i>"+vv1["work"]+"</i>, "+vv1["ref"]+"</b><span style='padding-left: 50px; display:block'><br>&emsp;Tagged with subjects: "+vv1["subject"]+"<br><br>&emsp;Found in books: "+vv1["book bibliographic info"]+", pages: "+vv1["page"]+"</span><br><br><table style='font-family:Palatino;background-color:white;'><tr style='font-family:Palatino;background-color:white;'><td style='min-width:600px;font-family:Palatino;background-color:white;'>"+vv1["refengcite"]+"</td></table>"

              else:
                  vv1["Index1"] =vv1.index
                  vv1["Index1"]=vv1["Index1"]+1
                  vv1["results"] = "<b>&emsp;"+vv1["Index1"].astype(str)+". "+vv1["author"]+", <i>"+vv1["work"]+"</i>, "+vv1["ref"]+"</b><span style='padding-left: 50px; display:block'><br>&emsp;Tagged with subjects: "+vv1["subject"]+"<br><br>&emsp;Found in books: "+vv1["book bibliographic info"]+", pages: "+vv1["page"]+"</span><br><br>"
              vv1 = vv1[['results']]
          else:
            kk["book 1"] = kk["book 1 info"]+", "+kk["page 1"]
            kk["book 2"] = kk["book 2 info"]+", "+kk["page 2"]
            #check = kk
            kk["results"] = kk["author"]+", <i>"+kk["work"]+"</i>, "+kk["ref"]+"<br><br>    Tagged with subjects: "+kk["subject 1"]+"<br>"+kk["subject 2"]+"<br><br>Found in books: "+kk["book 1"]+"; "+kk["book 2"]
            kk = kk[['results']]
            if len(vv1)!=0:
              vv1["Index1"] =vv1.index
              vv1["Index1"]=vv1["Index1"]+1
              vv1["results"] = vv1["Index1"].astype(str)+". "+vv1["author"]+", <i>"+vv1["work"]+"</i>, "+vv1["ref"]+"<br><br>    Tagged with subjects: "+vv1["subject 1"]+"<br>"+vv1["subject 2"]+"<br><br>"
              vv1["book 1"] = vv1["book 1 info"]+", "+vv1["page 1"]
              vv1["book 2"] = vv1["book 2 info"]+", "+vv1["page 2"]
              vv1 = vv1[['results','refcite','refengcite','book 1','book 2']]
          now12 = str(datetime.now())

      #fd = open("/home/moblid/mysite/emails.csv", "a")
      #fd.write("\n".join([now1,now2,now3,now4,now5,now6,now8,now9]))
      #fd.write("\n")
      #fd.close()




      #artart = artart[0:5]
      return render_template('index.html', ccs = ccs, ccs1 = ccs1, tablev=vv.to_html(escape=False, index=False), step="choose_upper", l = l, tablev1=vv1.to_html(escape=False, index=False), lengthvv1 = lengthvv1, tablek = kk.to_html(escape=False), yyy = yyy, fulltext=fulltext, cs=cs, ce=ce, lang=lang,author=author, work=work,ref=ref, lengthkk = lengthkk, Listkk=Listkk, empty=empty, lengthvv = lengthvv)

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
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

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
  height: 150px;
  width: 200px
}
}
#blackbox{
position:absolute;
top:0%;
left:0%;
width:85%;
height:100px;
margin-top:0px;
margin-left:15%;
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
<div class="w3-container">

<div class="w3-sidebar w3-bar-block w3-light-grey w3-card" style="width:15%">
  <br>
  <br>
  <br>
  <br>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Home</a>
  <a href="http://tiresias.haifa.ac.il/about" class="w3-bar-item w3-button w3-padding-24">About</a>
  <a href="http://tiresias.haifa.ac.il/network" class="w3-bar-item w3-button w3-padding-24">Network of subjects</a>
  <a href="http://tiresias.haifa.ac.il/biblio" class="w3-bar-item w3-button w3-padding-24">Book indices included</a>
  <a href="http://tiresias.haifa.ac.il/" class="w3-bar-item w3-button w3-padding-24">Search by subject</a>
  <a href="http://tiresias.haifa.ac.il/refs" class="w3-bar-item w3-button w3-padding-24">Search by reference</a>
  <a href="http://tiresias.haifa.ac.il/subjects" class="w3-bar-item w3-button w3-padding-24">Subject list</a>
  <a href="http://hcmh.haifa.ac.il/"><img src="/static/HCMH_logo_3_languages.png" alt="HCMH logo"></a>
</div>
</div>

<div style="margin-left:15%">

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
</font>

<br>

<div id="bottombox"><p>
                  <div align="center">
                  <br>
                  <input type="submit" value="Submit" style="width: 120px; height: 50px;" /  ><br>
                  </div>
                  </p>
                  </div>


<br>

<div style="text-align: justify; margin-left:5%; margin-right:5%">

                  The database is in its early stages of development, with many errors. Please use with caution. References are to texts between the 8th century BCE and the 8th century CE.
                  <br>The site is part of a digital humanities research project, conducted by Moshe Blidstein of the General History Department and the Haifa Center for Mediterranean History and Daphne Raban, the Department of Information & Knowledge Management, both at the University of Haifa. For information and suggestions, please contact mblidstei@univ.haifa.ac.il. <br>
                  <br>If you would like to receive updates on the development of the project, please enter your email and click "submit" above: <input type="text" name="email">
                  <br>For more information, see <a href="http://tiresias.haifa.ac.il/about">About</a>
                  <br>
                  </div>
              </form>'''
