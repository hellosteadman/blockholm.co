import adjust from './ratio'

document.querySelectorAll('.pagination-context').forEach(
    (container) => {
        const btn = container.querySelector('.btn-pagination')
        const grid = container.querySelector('.grid')
        let href = btn ? btn.getAttribute('href') : null
        let scrollTimer, loadTimer

        const go = () => {
            if (loadTimer) {
                return
            }

            fetch(href).then(
                (response) => {
                    response.text().then(
                        (html) => {
                            const fragment = document.createElement('html')

                            fragment.innerHTML = html

                            const newContainer = fragment.querySelector('.pagination-context')
                            const items = newContainer.querySelectorAll('.pagination-item')
                            const newBtn = newContainer.querySelector('.btn-pagination')
                            const appended = []

                            items.forEach(
                                (item) => {
                                    appended.push(grid.appendChild(item))
                                }
                            )

                            container.dispatchEvent(
                                new Event('ajax')
                            )

                            if (grid.classList.contains('grid-masonry')) {
                                grid.dispatchEvent(
                                    new CustomEvent(
                                        'masonry.append',
                                        {
                                            detail: {
                                                elements: appended,
                                                done: () => {
                                                    finish(newBtn)
                                                }
                                            }
                                        }
                                    )
                                )

                                loadTimer = setTimeout(
                                    () => {
                                        finish(newBtn)
                                    },
                                    5000
                                )
                            } else {
                                finish(newBtn)
                            }
                        }
                    )
                }
            ).catch(
                (err) => {
                    console.error(err)
                }
            )
        }

        const finish = (newBtn) => {
            if (newBtn) {
                href = newBtn.href
            } else {
                href = null
            }

            if (scrollTimer) {
                clearTimeout(scrollTimer)
                scrollTimer = null
            }

            if (loadTimer) {
                clearTimeout(loadTimer)
                loadTimer = null
            }
        }

        const trigger = () => {
            if (scrollTimer) {
                return
            }

            if (href) {
                scrollTimer = setTimeout(
                    () => {
                        go()
                        scrollTimer = null
                    },
                    1000
                )

                go()
            }
        }

        if (!btn) {
            return
        }

        document.addEventListener('scroll', 
            (e) => {
                const offset = container.offsetTop + container.clientHeight
                const pageOffset = window.pageYOffset + window.innerHeight

                if(pageOffset > offset - 100) {
                    trigger()
                }
            }
        )

        btn.parentNode.removeChild(btn)
    }
)
