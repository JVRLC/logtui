# Multiple sources

Pass several file paths to merge them into one live table:

```bash
logtui api.log worker.log nginx.log
```

The sidebar displays every source and its event count. Each normalized entry also
keeps its source name, including in the detail view.

All files are followed independently, so an idle source does not block active
ones.
