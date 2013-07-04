"""
Import rtm-formatted tasks through the RTM API.

This product uses the Remember The Milk API
but is not endorsed or certified by Remember The Milk.
"""

__docformat__ = 'reStructuredText'

import time

import rtm

class Importer(object):
  def import_tasks(self):
    self.timeline = self.rtm.timelines.create().timeline
    self.list_id  = self.rtm.lists.add(timeline=self.timeline,
      name='Dear Astrid ' + time.time()).list.id

    for task in tasks:
      self.add_task(task)

  def add_task(self, task):
    added = self.rtm.tasks.add(timeline=timeline, name=task['name'], parse=0)

    args = dict(
      timeline      = self.timeline,
      list_id       = self.list_id,
      taskseries_id = added.list.taskseries.id,
      task_id       = added.list.taskseries.task.id,
    )

    # Should this be setTags?
    rtm.tasks.addTags(tags=','.join(task['tags']), **args)

    if task['due_date']:
      # TODO: Can we determine has_due_time?
      rtm.tasks.setDueDate(due=task['due_date'], has_due_time=1, parse=0, **args)

    if task['estimated']:
      rtm.tasks.setEstmate(estimate=task['estimate'], **args)

    if task['priority']:
      rtm.tasks.setPriority(priority=task['priority'], **args)

    if task['repeat']:
      rtm.tasks.setRecurrence(repeat=task['repeat'], **args)

    if task['notes']:
      for note in task['notes']:
        rtm.tasks.notes.add(note_title=note, note_text=note, **args)

    # TODO: does Astrid do URLs? rtm.setURL(url=task['url'], **args)

    # do the status changes last
    if task['completed']:
      rtm.tasks.complete(**args)

    if task['deleted']:
      rtm.tasks.delete(**args)

    return added
