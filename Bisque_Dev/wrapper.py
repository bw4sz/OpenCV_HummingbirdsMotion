#!/bin/env python

import os
import sys
import logging
import glob
import re
import bq.api
import gobject

img_url_tag ='image.url'
staging_path= None
named_args={}
if __name__=='__main__':
	self_name=re.match(r'(.*)\.py$',sys.argv[0]).group(1)
	log_fn=self_name + '.log'
	logging.basicConfig(filename=log_fn,level=logging.WARNING)
	logging.debug('Script invocation: ' + str(sys.argv)
	for arg in sys.argv[1:]:
		tag,sep,val=arg.partition('=')
		if sep != '=':
			error_msg = 'malformed argument; + arg
			logging.error(error_msg)
			raise Exception(error_msg)
		named_args[tag]=val
		logging.debug('parsed a named arg' + str(tag) + '=' + str(val))
	murl = 'mex_url'
	btoken = 'bisque_token'
	for required_arg in [btoken,murl,img_url_tag]:
		if required_arg not in named_args:
			error_msg = 'missing mandatory argument' + required_arg
			logging.error(error_msg)
			raise Excpetion(error_msg)
	#Staging
	stage_tag ='staging_path'
	if stage_tag in named_args:
		staging_path = named_args[stage_tag]
		del named_args[stage_tag]
	else:
		staging_path = os.getcwd()
	#connect to bisque
	logging.debug('init bqsession, mex url=' + str(named_args[murl]) + 'and auth_token=' + str(named_args[btoken])
	
	#start session
	bqsession = bq.api.BQSession().init_mex(named_args[murl],named_args[btoken])
	del named_args[murl]
	del named_args[btoken]
	
	#try function
	try:
		outputs = test_find_points(bqsession , named_args[img_url_tag] )
 	except Exception as e:
 		logging.exception(str(e))
		bqsession.fail_mex(str(e))
	else:
		bqsession.finish_mex(tags =[outputs])

#define functions
def build these opts ( option_names ):
	return [’−−’ + x + ’=’ + str( named_args [x]) for x in named_args ]
	
def build incantation ():
	logging.debug(’assembling the incantation’)
	incantation = [os.path.join( staging_path , 'MotionMeerkat’)]  
	##This is confusing to me, not sure where to diverge from the find points example in the tutorial
	return [incantation]
	
def test_find_points(bqs):
	bqs.update_mex('testing incantation')
	incantation = build_incantation()
	logging.debug('assembled incantation:' + incantation)
	

