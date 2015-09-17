import os
import sys
from bqapi import BQSession, BQTag, BQFactory
from bqapi.util import fetch_dataset, fetch_blob, fetch_image_pixels
import logging
from subprocess import call
import re



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
    def main(self, image_url,  mex_url = None, bisque_token=None, bq = None, args = None):
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, bisque_token)
        # Fetch the blob  links
        if not os.path.exists ('videos'):
            os.makedirs ('videos')
        video = fetch_blob(bq, image_url, 'videos')
        print "VIDEO file ", video
	 #pass arguments to MotionMeerkat scripts, located in MotionMeerkat/main.py	
	#Structure arguments
	#Format call string

        callargs = ["python MotionMeerkat/main.py", 
                    "--i", video.values()[0], 
                    "--threshT", args[0],
                    "--sub", args[1],
                    "--mogh", args[2],
                    "--mogv", args[3],
                    "--accA", args[4],
                    "--burn", args[5],
                    "--frameSET", 
                    "--frame_rate", "1",
                    "--makeV", "none",
                    "--fileD", "Output"]
	print "Calling ", " ".join(callargs)

	#run MotionMeerkat
	r =  call(" ".join(callargs), shell=True)
        if r != 0:
		bq.fail_mex ("Meerkat returned non-zero")
		#Post Results
	frames_blob = bq.postblob("Output/Bfladefend_Converted/Frames.csv")
	#get file location from regex
	uri=re.search("uri=\"(.*?)\"", frames_blob).group(1)
	tags = [{ 'name': 'outputs','tag' : [{'name': 'frames_csv', 'type':'file', 'value':uri}]}]
	bq.finish_mex(tags = tags)
	sys.exit(0)

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
        args = args[3:]
        M.main(image_url, mex_url, auth_token, args = args)
    else:
        image_url = args.pop(0)

        if not options.credentials:
            parser.error('need credentials')
        user,pwd = options.credentials.split(':')

        bq = BQSession().init_local(user, pwd)
        M.main(image_url, bq=bq, args=args)



