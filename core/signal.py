from django.dispatch import receiver
from import_export.signals import post_import, post_export


@receiver(post_import, dispatch_uid='balabala...')
def _post_import(model, **kwargs):
    print("..........Post Import")
    print(kwargs)
    print(model)
    # for 
    # h = end.split(":")
    # end = (int(h[0]) + int(h[1]))/60
    # h = start.split(":")
    # start = (int(h[0]) + int(h[1]))/60
    # worked = end - start - paused

    # model is the actual model instance which after import
    pass


@receiver(post_export, dispatch_uid='balabala...')
def _post_export(model, **kwargs):
    print("..........Post Export")
    # model is the actual model instance which after export
    pass