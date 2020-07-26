def job_status_listener(event):
    if hasattr(event, 'exception'):
        if event.exception:
            print('The job crashed')
    print(event)
