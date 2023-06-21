document.addEventListener("DOMContentLoaded", () => {
    // Theme_Switcher_AJAX
    const themeSwitcherElement = document.querySelector('#themeSwitcher')
    themeSwitcherElement.addEventListener('click', () => {
        let htmlThemeElement = document.documentElement
        htmlThemeElement.dataset.bsTheme = htmlThemeElement.dataset.bsTheme === 'light' ? 'dark' : 'light';
        fetch('update_session/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'x-requested-with': 'XMLHttpRequest',
                'Content-Type': 'application/json;charset=utf-8',
            },
            credentials: 'include',
            body: JSON.stringify({theme: htmlThemeElement.dataset.bsTheme})
        })
    });

    // Content_Update
    const tags = document.querySelectorAll('#input-tags input[name="tags"]')

    tags.forEach((tag) => {
        tag.addEventListener('click', () => {
            deactivateOtherTags(tag)
            let params = ''
            if (tag.checked) {
                params = '?' + new URLSearchParams({tags: tag.value})
            }
            fetch(`update_content/${params}`, {
                headers: {
                    'x-requested-with': 'XMLHttpRequest',
                },
            }).then(response => response.json())
                .then(data => {
                    document.querySelector('#post-row').innerHTML = data.content
                });
        });
    });

    const searchForm = document.querySelector('#input-main')

    searchForm.addEventListener('change', (e) => {
        e.preventDefault()
        let params = ''
        const searchQuery = document.querySelector('#search-main').value
        if (searchQuery) {
            params = '?' + new URLSearchParams({search: searchQuery})
        }
        fetch(`update_content/${params}`, {
            headers: {
                'x-requested-with': 'XMLHttpRequest',
            },
        }).then(response => response.json())
            .then(data => {
                document.querySelector('#post-row').innerHTML = data.content
                deactivateTags()
                activateTags(data.tags)
            });
    })
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault()
    })

    function activateTags(tags) {
        tags.forEach((tag) => {
            const selector = `input[id="${tag}"]`
            document.querySelector(selector).checked = true
        });
    }

    function deactivateTags() {
        tags.forEach((tag) => {
            tag.checked = false
        });
    }

    function deactivateOtherTags(tag_to_avoid) {
        tags.forEach((tag) => {
            if (tag !== tag_to_avoid) {
               tag.checked = false
            }
        });
    }
    //Tag Create Modal
    // const createTagForm = document.querySelector('#create-tag-form')

    // createTagForm.addEventListener('submit', () => {
    //     const tag =  createTagInput.value
    //     // fetch('update_session/', {
    //     //     method: 'POST',
    //     //     headers: {
    //     //         'X-CSRFToken': getCookie('csrftoken'),
    //     //         'x-requested-with': 'XMLHttpRequest',
    //     //         'Content-Type': 'application/json;charset=utf-8',
    //     //     },
    //     //     credentials: 'include',
    //     //     body: JSON.stringify({tag: htmlThemeElement.dataset.bsTheme})
    //     // })
    //
    // });


    //From Django Docs for CSRF_Token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

