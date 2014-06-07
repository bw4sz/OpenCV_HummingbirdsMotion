
#include "Method.h"

Method::Method(const VideoFolder &videoFolder)
	: videoFolder(videoFolder)
{
	const cv::Mat frame = cv::imread(videoFolder.firstFrame());
	frameSize = frame.size();
}

Method::~Method() {}

void Method::process() {
	const Range range = videoFolder.getRange();
	process(range.first, range.second);
}

void Method::process(const uint fromIdx, const uint toIdx) {
	train(1, fromIdx - 1);
	detect(fromIdx, toIdx, fromIdx);
}
