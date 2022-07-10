📄 Examples
============

- Initialize the client:

.. code-block:: python

    me = Me(phone_number='+972123456789') # your phone number


- Basic phone search:

.. code-block:: python

    phones = ['+972123456789', '+972123456789', '+972123456789']
    for phone in phones:
        try:
            res = me.phone_search(phone)
            if res:
                print(res.name, res.phone_number)
                continue
            print('No match for {}'.format(phone))
        except MeApiException as e:
            if e.msg == 'api_search_passed_limit':
                print('passed limit for phone searches')
                break

- Advanced profile view:

.. code-block:: python

    try:
        profile: Profile = me.phone_search(phone_number=9721234567890).get_profile()
        if profile:
            print(profile.name,
                  profile.email,
                  profile.slogan,
                  profile.gender,
                  profile.profile_picture,
                  profile.user_type,
                  profile.location_name,
                  profile.age,
                  profile.carrier,
                  profile.device_type)
    except MeApiException as e:
        if e.msg == 'api_profile_view_passed_limit':
            print('profile view limit reached')

- Get social networks:

.. code-block:: python

    # profile (from previous example)
    socials = profile.social
    if socials.twitter.is_active:
        print(socials.twitter.profile_id)
    if socials.spotify.is_active:
        print(socials.spotify.profile_id)
    if socials.instagram.is_active:
        print(socials.instagram.profile_id)
    if socials.tiktok.is_active:
        print(socials.tiktok.profile_id)

- Approve and like all the comments posted on your profile:

.. code-block:: python

    for comment in me.get_comments():
        print(comment.author.name, comment.message)
        if comment.status == 'waiting':
            comment.approve()
        comment.like()
