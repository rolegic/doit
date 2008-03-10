import os
import anydbm

from doit.util import md5sum

class Dependency(object):
    """ Dependency manager. 
    Each dependency is a saved in dbm. where the key is taskId + dependency (abs file path), and the value is the dependency signature.
    """

    #TODO lazy open DBM.
    def __init__(self, name, new=False):
        """open/create a DBM
        @param name string filepath of the DBM file
        @param new boolean always create a new empty database
        """
        self.name = name
        self._closed = False
        if new:
            self._db = anydbm.open(name,'n')
        else:
            self._db = anydbm.open(name,'c')


    def __del__(self):
        self.close()

    def _set(self, taskId, dependency, value):
        """ store value in the DBM"""
        self._db[taskId+dependency] = value

    def _get(self, taskId, dependency):
        """ @return value stored in the DBM, return None if entry not found"""
        return self._db.get(taskId+dependency,None)

    def save(self, taskId, dependency):
        """ save/update dependency on the DB.
        this method will calculate the value to be stored using md5 and then
        call the _set method.
        """
        self._set(taskId,dependency,md5sum(dependency))

    def modified(self,taskId, dependency):
        """ @return bool if dependency for task was modified or not"""
        return self._get(taskId,dependency) != md5sum(dependency)

    def close(self):
        if not self._closed:
            self._db.close()
            self._closed = True

    def save_dependencies(self,taskId, dependencies):
        """save dependencies value.
        @param taskId  string
        @param dependencies list of string 
        """
        for d in dependencies:
            self.save(taskId,d)

    def up_to_date(self, taskId, dependencies, targets):
        """check if task is up to date
        @param taskId  string
        @param dependencies list of string 
        @return bool True if up to date, False needs to re-execute.
        """
        # no dependencies means it is never up to date.
        if not dependencies:
            return False

        # if target file is not there, task is not up to date
        for t in targets:
            if not os.path.exists(t):
                return False

        # check for dependencies 
        for d in tuple(dependencies) + tuple(targets):
            if self.modified(taskId,d):
                return False
                
        return True
