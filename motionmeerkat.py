import os
import sys
from bqapi import BQSession, BQTag, BQFactory
from bqapi.util import fetch_dataset, fetch_blob, fetch_image_pixels
import logging
from subprocess import call

logging.basicConfig(filename='motionmeerkat.log',level=logging.DEBUG)

def fetch_dataset (bq, uri, destdir):
    """ Fetch the binaries associated with a bisque dataset
    @param bq: A BQSession object
    @param uri: a dataset uri 
    @param destdir: directory to put the binaries in
    @return :  A dict mapping a blob uri -> binary filename 
    """
    # Get the elements of the dataset as xml entries
    dataset = bq.fetchxml("%s/value" %uri)
    results = {}
    # loop through each element i.e each image/video to fetch the binary
    for fxml  in dataset:
        # get the unique uri of the blob
        furi = fxml.get ('uri')  
        logging.debug( "FETCHING %s", furi)
        # sanity check that we are fetching something that has a binary component
        if  fxml.tag == 'file' or fxml.tag == 'image':
            x = fetch_blob(bq, furi, dest=destdir)
        #elif fxml.tag == 'image':
        #    x = fetch_image_pixels(bq, furi, dest=destdir)
        else:
            logging.warn ('skipping %s', BQFactory.to_string(fxml))
            continue
        results.update (x)
    return results


class motionmeerkatModule(object):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    def main(self, image_url,  mex_url = None, bisque_token=None, bq = None):
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, bisque_token)
        # Fetch the datasets  links

        if not os.path.exists ('videos'):
            os.makedirs ('videos')
        dataset = fetch_dataset (bq, image_url, 'videos')
        print "DATASET", dataset
	print 'File to run:', dataset.values()[0]
	 #pass arguments to MotionMeerkat scripts, located in MotionMeerkat/main.py
	print args
	
	#Structure arguments
	inDest=dataset.values()[0]	
	args.insert(3,inDest)

	#Format call string
	callargs=str("python MotionMeerkat/main.py --i %s --threshT %s --sub %s --mogh %s --mogv %s --accA %s --burn %s --frameSET --frame_rate 1 --makeV none" %tuple(args[3:]))
	print callargs

	#run MotionMeerkat
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



