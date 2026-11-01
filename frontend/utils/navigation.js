// Direct links and reLaunch can leave a page without a previous stack entry.
export function navigateBack(fallbackUrl = '/pages/home/Home', isTab = true) {
	const fallback = () => {
		if (isTab) uni.switchTab({ url: fallbackUrl })
		else uni.reLaunch({ url: fallbackUrl })
	}
	if (getCurrentPages().length > 1) {
		uni.navigateBack({ delta: 1, fail: fallback })
	} else {
		fallback()
	}
}
