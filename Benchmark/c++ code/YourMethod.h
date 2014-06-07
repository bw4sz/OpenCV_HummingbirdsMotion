
#pragma once

#include "Method.h"

class YourMethod : public Method
{
	public:
		YourMethod(const VideoFolder &videoFolder, const Arguments& arguments);
		~YourMethod();

		virtual void train(const uint fromIdx, const uint toIdx);
		virtual void detect(const uint fromIdx, const uint toIdx, const uint startSavingAt);

	private:
		// TODO Create constants and variables
};

