# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
   # response.flash = T("Welcome to RedditSIM")
    return dict(message='')


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in 
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
def login():
	return dict(form=auth.login())

def index():
	form=db().select(db.posts.ALL,orderby=~db.posts.votes)
	return dict(form=form)
@auth.requires_login()
def posts():
	form=SQLFORM(db.posts)
	
	if form.process().accepted:

	#		post=db(db.posts.id>0).select().last()
	#		db(db.posts.id==post.id).delete()
	#		response.flash = 'INCORRECT URL'
		some=db(db.posts.id>0).select().last()
		some.user_id=auth.user.id
		some.update_record()
		session.flash = 'POST SUBMITTED'
		redirect(URL('index'))
	return dict(form=form)

def show_cat():
	form=db().select(db.posts.ALL)
	return dict(form=form)

def post_bycat():
	#print request.args(0,cast=str)
	form=db(db.posts.category==request.args(0,cast=str)).select(orderby=~db.posts.votes)
	return dict(form=form)
def voting():

	flag=False
	ans=request.args(1,cast=int)
	#print request.args(0),request.args(1)
	post=db(db.posts.id==request.args(0,cast=str)).select().first()
	userm=db((db.liked.user_id==auth.user.id) &(db.liked.post_id==post.id)).select()
	if(len(userm)==0):
		flag=True
	if(len(userm)==1):
		if ans==1 and userm[0].response==False:
			flag=False
			post.votes += 8
			post.update_record()
			userm[0].response=True
			userm[0].update_record()
			session.flash = 'Response Changed'
			redirect(URL('post_bycat',args=post.category))
	
		if ans==-1 and userm[0].response==True:
			flag=False
			post.votes -= 8
			post.update_record()
			userm[0].response=False
			userm[0].update_record()
			session.flash = 'Response Changed'
			redirect(URL('post_bycat',args=post.category))
	if flag:
		if(ans==1):
			post.votes += 5
			db.liked.insert(user_id=auth.user.id,post_id=post.id,response=True)
		elif(ans==-1):
			post.votes -= 3
			db.liked.insert(user_id=auth.user.id,post_id=post.id,response=False)
		
		session.flash = 'Response Recorded'
		post.update_record()
		redirect(URL('post_bycat',args=post.category))
	else:
		session.flash = 'Already responded to post'
		redirect(URL('post_bycat',args=post.category))

	return dict()
def myposts():
	form=db(db.posts.user_id==auth.user.id).select()

	return dict(form=form)

def delp():
	db(db.posts.id==request.args(0,cast=str)).delete()
	session.flash = 'Post Deleted'
	redirect(URL('myposts'))
	
	return dict()

def editp():
	db.posts.url.writable=False
	post=db(db.posts.id==request.args(0,cast=str)).select().first()
	caty=db(db.caty.id>0).select()	
	form = SQLFORM.factory(
				Field('title',type='string',length=128,default=post.title),
				Field('url',writable=False,default=post.url),
				Field('category',length=128,default=post.category,requires=IS_IN_DB(db,'caty.id','caty.category_name'))
	)
	if form.process().accepted:
		a=request.vars.category.split()
		if (len(a))>1:
			session.flash = 'Category can only be one word!'
		else:
			db(db.posts.id==post.id).update(title=form.vars.title,category=form.vars.category)
			session.flash = 'Changes Complete'

		redirect(URL('editp',args=post.id))

	return dict(form=form,some=post)
import datetime
def post_comet():
	some=db(db.posts.id==request.args(0,cast=str)).select().first()
	form = SQLFORM.factory(
				Field('post_comment',type='text',default=''))
	if form.process().accepted:
			db.comments.insert(user_id=auth.user.id,post_id=some.id,comet=form.vars.post_comment,time_posted=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
			session.flash = 'Comment Posted'
			redirect(URL(post_comet,args=some.id))
	return dict(some=some,form=form)
def add_caty():
	
	form = SQLFORM(db.caty)

	if form.process().accepted:
		a=form.vars.category_name.split()
		if (len(a))>1:
			delu=db(db.caty.id>0).select().last()
			db(db.caty.id==delu.id).delete()	
			response.flash = 'Category can only be one word!'
		else:
			response.flash = 'Category Added'


	return dict(form=form)
def admin_stuff():
	return dict()
def uedit_all():
	
	alluser=db(db.auth_user.id>0).select(orderby=db.auth_user.first_name)
	return dict(form=alluser)
def pedit_all():
	
	allpost=db(db.posts.id>0).select(orderby=~db.posts.votes)
	return dict(form=allpost)

def delpost():
	db(db.posts.id==request.args(0,cast=int)).delete()
	session.flash='Post Deleted'
	redirect(URL(pedit_all))
def deluser():
	db(db.auth_user.id==request.args(0,cast=int)).delete()
	session.flash='User Account,Posts,Comments Deleted'
	redirect(URL(uedit_all))
	

