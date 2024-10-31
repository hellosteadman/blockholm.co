document.querySelectorAll('.video-block').forEach(
    (container) => {
        const player = container.querySelector('video')
        const elapsed = container.querySelector('.elapsed')
        const duration = container.querySelector('.duration')
        const seek = container.querySelector('input[type="range"]')
        const enable = () => {
            container.querySelectorAll('button[disabled], input[disabled]').forEach(
                (control) => {
                    control.classList.remove('disabled')
                    control.disabled = false
                }
            )
        }

        const disable = () => {
            container.querySelectorAll('button, input').forEach(
                (control) => {
                    control.classList.add('disabled')
                    control.disabled = true
                }
            )
        }

        const showTime = () => {
            elapsed.textContent = new Date(player.currentTime * 1000).toISOString().substr(11, 8)
            duration.textContent = new Date(player.duration * 1000).toISOString().substr(11, 8)
        }

        const volume = player.volume
        let idleTimer = null

        player.addEventListener('canplay', enable)
        player.addEventListener('canplaythrough', enable)
        player.addEventListener('waiting', disable)
        player.addEventListener('durationchange',
            () => {
                if (player.duration) {
                    enable()
                }

                showTime()
            }
        )

        player.addEventListener('timeupdate',
            () => {
                seek.value = (player.currentTime / player.duration) * 100
                showTime()
            }
        )

        player.addEventListener('play',
            () => {
                container.classList.add('playing')
                container.classList.remove('paused')
                container.classList.remove('ready')
            }
        )

        player.addEventListener('volumechange',
            () => {
                if (player.volume === 0) {
                    container.classList.add('muted')
                } else {
                    container.classList.remove('muted')
                }
            }
        )

        player.addEventListener('pause',
            () => {
                container.classList.remove('playing')
                container.classList.add('paused')
            }
        )

        player.addEventListener('ended',
            () => {
                container.classList.remove('playing')
                container.classList.add('ready')
            }
        )

        container.addEventListener('click',
            (e) => {
                if (e.target.disabled) {
                    e.preventDefault()
                    return
                }

                if (idleTimer) {
                    clearTimeout(idleTimer)
                    container.classList.remove('idle')
                }

                if (e.target.matches('.btn-play') || e.target.closest('.btn-play')) {
                    player.play()
                    return
                }

                if (e.target.matches('.btn-pause') || e.target.closest('.btn-pause')) {
                    player.pause()
                    return
                }

                if (e.target.matches('.btn-mute') || e.target.closest('.btn-mute')) {
                    player.volume = 0
                    return
                }

                if (e.target.matches('.btn-unmute') || e.target.closest('.btn-unmute')) {
                    player.volume = volume
                    return
                }

                if (e.target.matches('button') || e.target.closest('button')) {
                    return
                }

                if (e.target.matches('input') || e.target.closest('input')) {
                    return
                }

                if (e.target.matches('.controls') || e.target.closest('.controls')) {
                    return
                }

                if (!player.paused && !player.ended) {
                    player.pause()
                } else {
                    player.play()
                }
            }
        )

        seek.addEventListener('input',
            () => {
                player.currentTime = (seek.value / 100) * player.duration
            }
        )

        container.addEventListener('mousemove',
            () => {
                if (player.paused || player.ended) {
                    if (idleTimer) {
                        clearTimeout(idleTimer)
                        container.classList.remove('idle')
                    }

                    return
                }

                if (idleTimer) {
                    clearTimeout(idleTimer)
                    container.classList.remove('idle')
                }

                idleTimer = setTimeout(
                    () => {
                        container.classList.add('idle')
                    },
                    3000
                )
            }
        )

        container.classList.add('ready')
    }
)
