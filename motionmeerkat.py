import os
import sys
from bqapi import BQSession, BQTag
from bqapi.util import fetch_dataset
import logging
from subprocess import call

logging.basicConfig(filename='motionmeerkat.log',level=logging.DEBUG)

class motionmeerkatModule(object):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    def main(self, image_url,  mex_url = None, bisque_token=None, bq = None):
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, bisque_token)
        # Fetch the datasets  links

        if not os.path.exists ('images'):
            os.makedirs ('images')
        dataset = fetch_dataset (bq, image_url, 'images')
        print dataset
	 #pass arguments to MotionMeerkat scripts, located in MotionMeerkat/main.py
	print args
	#Structure arguments
	inDest='MotionMeerkat/PlotwatcherTest.avi'	

	#Format call string
	args.insert(3,inDest)
	callargs=str("python MotionMeerkat/main.py --i %s --theshT %s --sub %s --mogh %s --mogv %s --accA %s --burn %s" %tuple(args[3:]))
	print callargs
	print call([callargs],shell=True)

	

	
        # Fetch embedded tags from image service
        #meta = image.pixels().meta().fetch()
        #meta = ET.XML(meta)
        #tags = []
        # Create a new tag 'MetaData' to be placed on the image
        #md = BQTag(name='MetaData')
        # Filter the embedded metadata and place subtags in MetaData
        #for t in meta.getiterator('tag'):
        #    if t.get('name') in wanted_tags:
        #        md.addTag (name=t.get('name'),
        #                   value=t.get('value'))
        ## Add the new tag to the image
        #image.addTag(tag = md)
        #metadata_tag = bq.save(md, image.uri + "/tag")
        #if metadata_tag is None:
        #    bq.fail_mex ("could not write tag: no write access")
        #    return
        #bq.finish_mex(tags = [{ 'name': 'outputs',
        #                        'tag' : [{ 'name': 'metadata',
        #                                   'value': metadata_tag.uri,
        #                                   'type' : 'tag' }]}])
        bq.finish_mex()
        sys.exit(0)
        #bq.close()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c", "--credentials", dest="credentials",
                      help="credentials are in the form user:password")
    #parser.add_option('--image_url')
    #parser.add_option('--mex_url')
    #parser.add_option('--auth_token')

    (options, args) = parser.parse_args()

    M = motionmeerkatModule()
    if options.credentials is None:
        mex_url,  auth_token, image_url  = args[:3]
        M.main(image_url, mex_url, auth_token)
    else:
        image_url = args.pop(0)

        if not options.credentials:
            parser.error('need credentials')
        user,pwd = options.credentials.split(':')

        bq = BQSession().init_local(user, pwd)
        M.main(image_url, bq=bq)



