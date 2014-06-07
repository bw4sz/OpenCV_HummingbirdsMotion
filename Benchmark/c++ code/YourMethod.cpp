
#include "YourMethod.h"

YourMethod::YourMethod(const VideoFolder &videoFolder, const Arguments& arguments)
	: Method(videoFolder)
{
	// TODO Initialization

	// In the YourMethod class, you can use 
	//   -videoFolder : get the path of input and binary frames
	//      with opencv : cv::imread(videoFolder.inputFrame(t));
	//   -frameSize : get the size (width, height)
}


YourMethod::~YourMethod() {
	// TODO Cleaning
}

void YourMethod::train(const uint fromIdx, const uint toIdx) {
	// TODO Training
	// If your method requires no special code for training, we call detect
	detect(1, toIdx, toIdx + 1);
}

void YourMethod::detect(const uint fromIdx, const uint toIdx, const uint startSavingAt) {
	/* You can work the way you want. This code shows how to iterate over all the pixels */
	BinaryFrame binaryFrame(frameSize, CV_8UC1);
	for (uint t = fromIdx; t < toIdx; ++t) {
		binaryFrame = BLACK;

		InputFrame inputFrame = cv::imread(videoFolder.inputFrame(t));

		BinaryIterator itBinary = binaryFrame.begin();
		InputIterator itEnd = inputFrame.end();
		for (InputIterator itInput = inputFrame.begin(); itInput != itEnd; ++itInput, ++itBinary) {
			//const cv::Vec3d pixel = *itInput;
			//const uchar red = pixel[0];
			//const uchar green = pixel[1];
			//const uchar blue = pixel[2]; 
			//
			//
			//if (...) {
			//	*itBinary = WHITE;
			//}
		}

		if (t >= startSavingAt) {
			//cv::medianBlur(binaryFrame, binaryFrame, 5);
			cv::imwrite(videoFolder.binaryFrame(t), binaryFrame);
		}

		// Update model
		// 
	}
}
