# Created by kurush at 13.12.2021

@fixture.running.server
Feature: Managing user account
  Getting access to user account

  Background:
    Given "auth_service" runs on "http://localhost:9000/"
    And "search_service" runs on "http://localhost:9001/"
    And "scout_service" runs on "http://localhost:9002/"
    And cite client exists

  Scenario Outline: Login
    Given user is at "login" page
    When user enters <username>  and <password> in request form
    Then user's login status is <status>

    Examples: Credentials
      | username | password | status |
      | user1    | pass1    | True   |
      | user123  | xyz      | False  |


  Scenario: Successful request of account page
    Given user is logged in with credentials
    """
    {
    "username": "user1",
    "password": "pass1"
    }
    """
    And user visited "book" page with id = "1"
    When user goes to "account" page
    Then user gets user info
    And user gets card of "book" with id = "1"