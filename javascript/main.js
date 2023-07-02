function submit_sc_loader(){
    var id = randomId()
    localStorage.setItem('sc_loader_task_id', id)

    requestProgress(
        id,
        gradioApp().getElementById('sc_loader_gallery_container'),
        gradioApp().getElementById('sc_loader_gallery'),
        () => { localStorage.removeItem('sc_loader_task_id') }
    )

    var res = create_submit_args(arguments)

    res[0] = id

    return res
}