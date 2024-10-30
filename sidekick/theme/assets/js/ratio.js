export default (container) => {
    const containerWidth = container.clientWidth
    const iframe = container.tagName === 'IFRAME' ? container : container.querySelector('iframe')

    if (!iframe) {
        container.classList.remove('ratio-unknown')
        container.classList.remove('ratio')
        return
    }

    let iframeWidth = iframe.getAttribute('width')
    let iframeHeight = iframe.getAttribute('height')

    if (iframeWidth !== null) {
        iframeWidth = iframeWidth.toString()
    }

    if (iframeHeight !== null) {
        iframeHeight = iframeHeight.toString()
    }

    if (iframeWidth.substr(iframeWidth.length - 2) === 'px') {
        iframeWidth = iframeWidth.substr(0, iframeWidth.length - 2)
    }

    if (iframeWidth.substr(iframeWidth.length - 1) == '%') {
        const percent = parseInt(iframeWidth.substr(0, iframeWidth.length - 1))
        
        if (!iframeHeight) {
            iframeWidth = containerWidth / 100 * percent
            iframeHeight = parseInt(iframeWidth / 16 * 9)
        } else {
            container.classList.remove('ratio-unknown')
            container.classList.remove('ratio')
            return
        }
    } else if (iframeHeight.substr(iframeHeight.length - 2) == 'px') {
        iframeHeight = iframeHeight.substr(0, iframeHeight.length - 2)
    }

    iframeWidth = parseInt(iframeWidth)
    iframeHeight = parseInt(iframeHeight)

    if (isNaN(iframeWidth) || isNaN(iframeHeight)) {
        container.classList.remove('ratio-unknown')
        container.classList.remove('ratio')
        return
    }

    iframeHeight = parseInt(containerWidth / iframeWidth * iframeHeight)
    iframe.setAttribute('width', containerWidth)
    iframe.setAttribute('height', iframeHeight)
    container.style.height = `${iframeHeight}px`
}
