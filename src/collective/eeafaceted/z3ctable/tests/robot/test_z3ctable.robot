*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging

Suite Setup  Suite Setup
Suite Teardown  Close all browsers

Test Setup  Test Setup

*** Test cases ***

Test Add Faceted Collection Portlet
    Go to  ${PLONE_URL}/eea


*** Keywords ***
Suite Setup
    Open test browser
    Enable autologin as  Manager

Test Setup
    Create content  type=Collection  id=first  title=First Collection
    Create content  type=Collection  id=second  title=Second Collection
    Create content  type=Collection  id=third  title=Third Collection
    Create content  type=Folder  id=eea  title=Folder EEA
    
Close overlay
    Wait until element is visible  css=.overlay-ajax .close
    Click element  css=.overlay-ajax .close
