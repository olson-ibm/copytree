import unittest
import filecmp
import os
import shutil

import randomfiletree

from copytree import copytree

class test_copytree(unittest.TestCase):

    temp_home = '/tmp'
    source = os.path.join(temp_home, 'source')
    usr_local_bin = '/usr/local/bin'
    good_target_already_exists = os.path.join(temp_home, 'good')
    good_target_doesnt_exist = os.path.join(temp_home, 'does_not_exist')
    
    
    # owned_by_root is root:root, chmod 777 
    # This is created manually. See SetUp
    protected_target = os.path.join(temp_home, 'protected')

    
    def setUp(self):

        randomfiletree.iterative_gaussian_tree(
            self.source,
            nfiles=3.0,
            nfolders=3.0,
            maxdepth=3,
            repeat=2
        )

        # Need to run as root to do this? Set up manually for now
        #if not os.path.exists(self.protected_target):
        #    os.makedirs(self.good_target)
        # chown root:root
        # chmod 777

        if not os.path.exists(self.good_target_already_exists):
            os.makedirs(self.good_target_already_exists)
        


    def tearDown(self):
        try:
            # only one that should exist is the first. Remainder get
            # cleaned up when finished.
            shutil.rmtree(self.source)
            shutil.rmtree(self.good_target_already_exists)
            shutil.rmtree(self.good_target_doesnt_exist)
            self.clear_folder(self.protected_target)
        except Exception as e:
            pass

    def clear_folder(self, folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def are_dir_trees_equal(self, dir1, dir2):

        dirs_cmp = filecmp.dircmp(dir1, dir2)
        if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0 or \
            len(dirs_cmp.funny_files)>0:
            return False
        (_, mismatch, errors) =  filecmp.cmpfiles(
            dir1, dir2, dirs_cmp.common_files, shallow=False)
        if len(mismatch)>0 or len(errors)>0:
            return False
        for common_dir in dirs_cmp.common_dirs:
            new_dir1 = os.path.join(dir1, common_dir)
            new_dir2 = os.path.join(dir2, common_dir)
            if not self.are_dir_trees_equal(new_dir1, new_dir2):
                return False
        return True
    
  
    def test_are_dir_trees_equal_true(self):
        """
        Calibrate are_dir_trees_equal. This should return true
        """
        assert(self.are_dir_trees_equal(self.source, self.source))
    
    def test_are_dir_trees_equal_false(self):
        """
        Calibrate are_dir_trees_equal. This should return false
        """
        is_false = self.are_dir_trees_equal(self.source, self.usr_local_bin) 
        assert(is_false == False)
    
    def test_base_case_target_diretory_exists(self):
        """
        Target dir already exists, but is empty
        """
        copytree(self.source, self.good_target_already_exists)
        assert(self.are_dir_trees_equal(self.source, self.good_target_already_exists))

    def test_base_case_target_diretory_exists_and_is_already_populated(self):
        """
        Target dir already exists, but is already populated with the target copy
        (Run the above test again, then clean up)
        """
        copytree(self.source, self.good_target_already_exists)
        assert(self.are_dir_trees_equal(self.source, self.good_target_already_exists))
        shutil.rmtree(self.good_target_already_exists)
    
    def test_base_case_target_diretory_doesnt_exist(self):
        """
        Target dir does not exist
        """
        copytree(self.source, self.good_target_doesnt_exist)
        assert(self.are_dir_trees_equal(self.source, self.good_target_doesnt_exist))
        shutil.rmtree(self.good_target_doesnt_exist)
    
    def test_shutil_copytree_fail_case(self):
        """
        Original error case, prove we can reproduce it EXACTLY
        """
        with self.assertRaises(shutil.Error) as e:
            shutil.copytree(self.source, self.protected_target, dirs_exist_ok=True)
            assert(self.are_dir_trees_equal(self.source, self.protected_target))
        self.assertIn("[Errno 1] Operation not permitted", str(e.exception))
        self.clear_folder(self.protected_target)
        assert(len(os.listdir(self.protected_target)) == 0)

    def test_copytree_pass_case(self):
        """
        Original error case, prove we fixed it
        """
        copytree(self.source, self.protected_target)
        assert(self.are_dir_trees_equal(self.source, self.protected_target))
    
if __name__ == '__main__':
    unittest.main()
    
