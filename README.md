# opsdroid skill travis

A skill for [opsdroid](https://github.com/opsdroid/opsdroid) to notify on travis builds.

## Requirements

None.

## Configuration

```yaml
skills:
  - name: travis
    room: "#monitoring"  # (Optional) room to send alert to
    travis_endpoint: "org"  # (Optional) endpoint for travis, change to "com" if using enterprise Travis CI
```

## Usage

[Configure a webhook](https://docs.travis-ci.com/user/notifications/#Configuring-webhook-notifications) in your travis.yml which points to your opsdroid webhook.

```yaml
notifications:
  webhooks:
    urls:
      - http://example.com/skill/travis/event
```

## License

GNU General Public License Version 3 (GPLv3)
