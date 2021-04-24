# [Project Name]

## About

You have found the conference website we've written for FrOSCon 2020 (Cloud Edition) \o/

This code is (at least in some parts) really hacky. It was written over the span of just a few days and last fixes were applied during the conference itself.

Overall we were surprised how smoothly everything went, and we are glad to announce that we got an F(ull score :P) in some weird Mozilla privacy check, that's something we always wanted to have :)

Feel free to use the code for your own projects, but please don't come running back for support. At least for now everything here is just provided as is.

## Rough feature set

- Landing page
    - Introduction to the event and links to the actual overview
    - Links to overview can be disabled (`PAGE_LIVE`) so it can be linked without everybody clicking through to the unfinished event overview
    - Also shows event partners/sponsors so they are happy :)
- Manage BBB rooms over multiple servers, with following features for each room:
    - Manage moderator permissions
    - Lockdown (e.g. disable mics/webcams)
    - Enable/Disable recording
    - Pre-upload default slides
    - Set maximum number of participants
    - Collect stats (e.g. participant count was publicly visible on our site)
    - Set branding logo
    - Set welcome message
    - Ask for accepted dataprotectionfoo before joining a room being recorded
    - and more :)
- Custom announcements
    - Simple HTML written in admin backend to be visible at the top of the site
    - E.g. for a social event after the talks or for links to quizzes and merch
    - Announcements can be hidden so that they can be prepared in advance and enabled as needed
- Stream
    - Each lecture room can be assigned a stream id
    - If a stream is assigned instead of directly joinen the BBB room the stream will be shown with a link to the BBB room below
    - Currently using c3voc streaming-website code and pointing directly at the c3voc cdn, so if you want to use it for a private event you need to modify at least that
- Scheduling
    - Support for importing Frab schedule and person information
    - Integrated into event overview
    - Small script go generate BBB rooms for workshops
    - A bit of logic not to show all workshop rooms on the site at the same time
- Chat system
    - Support for multiple rooms (even though we just used `lobby`)
    - Support for whisper messages (only visible to recevier)
    - Minimal moderation features (invisible ban for spammers, we thankfully didn't need to even try if it works :D)
    - System chat announcements (a bit more visible than just writing a simple message)
    - and more :)
- Authentication
    - Allow guests to enter chat and bbb rooms using just a name (adds `guest-` prefix to name and a unique id at the end)
    - Allow registration/login using just a username and password (those users can e.g. be used to give moderator permissions in bbb)
    - Support for generating authentication tokens to allow login using a simple link
- Partners/Sponsors
    - Page for each partner with support for them to edit their own description
    - Own BBB room
    - Partner highlighted on event page if BBB room was active

## Possible future features

We might implement this stuff at some point, or we might not. PRs welecome ;)

* Name for the project
* Update current events, workshops, user count automatically
* announcements using markdown
* cleanup event overview lectures section to allow for none BBB lectures
* proper approach to translations
* no hardcoded froscon stuff
* ...