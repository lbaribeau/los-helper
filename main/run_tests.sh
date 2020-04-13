#!/bin/bash

#python -m unittest test.test_los_helper.TestLosHelper.test_silly
# python -m unittest discover -s main test.test_mob_target_determinator.TestMobTargetDeterminator.test_silly
#python -m unittest discover main test.test_mob_target_determinator.TestMobTargetDeterminator.test_silly
#python -m unittest discover main test.test_mob_target_determinator.TestMobTargetDeterminator.on_mob_arrival_should_increment
python3 -m unittest test.test_mob_target_determinator

