document.addEventListener('submit',
    (e) => {
        const captchaField = e.target.querySelector('input[data-recaptcha-key]')

        if (!captchaField) {
            return
        }

        const captchaKey = captchaField.getAttribute('data-recaptcha-key')
        e.preventDefault()
        e.stopPropagation()

        grecaptcha.ready(
            () => {
                grecaptcha.execute(
                    captchaKey,
                    {
                        action: 'submit'
                    }
                ).then(
                    (token) => {
                        captchaField.value = token
                        e.target.submit()
                    }
                ).catch(
                    () => {
                        e.target.submit()
                    }
                )
            }
        )
    }
)
