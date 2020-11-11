# from flask import Flask
from flask import *
app = Flask(__name__)

import json
import requests
from flask import render_template 

# Github API can return maximum 100 results in one API call.
# Thus we need to call API for each page of result.

def getContributors(m,base_url):
	#Function to Find Top M Contributors in a repository
	contributor_list=[]
	contrib_page=1
	tot=0
	try:
		while(True):
			contributor_url=base_url+str(contrib_page)+"&per_page=100"
			print(contributor_url)
			contributorss=requests.get(contributor_url).json()
			siz=len(contributorss)
			if siz==0:
				break
			# print(contributorss)
			for usr in contributorss:
				if tot>=m:
					break
				user=usr['login']
				tot_cont=usr['contributions']
				contributor_list.append([user, tot_cont])
				tot+=1
			if(tot>=m):
				break
			contrib_page+=1
		return contributor_list
	except:
		lis=[]
		return lis

@app.route('/getOrgDetails', methods=['POST', 'GET'])
def getOrgDetails():
	#Get All Repository List of organization
	#Sort Repository According to Stars
	#Get Top N repositories
	try:
		organization_name = request.form['orgzn']
		n = int(request.form['repo_count'])
		m = int(request.form['contrib_count'])
		print(organization_name,n,m)
		cnt=0
		pagecount=1
		repo_list=[]
		# Enter Token here
		tokn="xxxxxxxxxxxxxxxxxxxxxxx"
		while(True):
			paginated_url="https://api.github.com/orgs/"+organization_name+"/repos?access_token="+str(tokn)+"&page="+str(pagecount)+"&per_page=100"
			public_repos=requests.get(paginated_url).json()
			print(len(public_repos))
			# print(public_repos)
			if(len(public_repos)==0):
				break
			for repo in public_repos:
				repo_name = repo['name']
				stars = repo['stargazers_count']
				repo_list.append([repo_name, stars])
			pagecount+=1
		print(len(repo_list))
		repo_list.sort(key=lambda x: x[1], reverse=True)
		n=min(n,len(repo_list))
		top_n_repo=repo_list[0:n]
		# to_n_repo list contain Most Popular N repositories
		finallist=[]
		for repp in top_n_repo:
			print(repp)
			#Get Top Contributors in this repository
			contributor_url="https://api.github.com/repos/"+organization_name+"/"+repp[0]+"/contributors?access_token="+str(tokn)+"&q=contributions&order=desc&page="
			li=getContributors(m,contributor_url)
			print(li)
			d1=dict()
			d1["RepoName"]=repp[0]
			d1["TopContributors"]=li
			json_object = json.dumps(d1, indent=4)
			resultt = json.loads(json_object)
			finallist.append(resultt)
		#return result in json format to render on html template
		return render_template("index.html", jsonList=finallist,organization_name=organization_name)
	except:
		return render_template("errormessage.html")

@app.route('/') 
def homepage():
    return render_template("inputform.html")
    # return render_template("index.html", jsonList=finallist) 

if __name__ == "__main__":
    app.run(host='0.0.0.0')
