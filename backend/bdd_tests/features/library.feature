# Created by kurush at 13.12.2021

@fixture.running.server
Feature: Requesting library pages
  Getting access to multiple cite pages containing info about books, series and authors.

  Background:
    Given "auth_service" runs on "http://localhost:9000/"
    And "search_service" runs on "http://localhost:9001/"
    And "scout_service" runs on "http://localhost:9002/"
    And cite client exists

  Scenario: Successfully request Home Page
    When user goes to "home" page
    Then user gets "multiple" cards of "author, series and book"

  Scenario: Successfully request Author Page
    Given user is at "home" page
    And user observes "author" card with id = "1"
    When user goes to "author" page with id = "1"
    Then user gets information about "author" with id = "1"
    And user gets "one" cards of "series"
    And user gets "multiple" cards of "book"

  Scenario: Successfully request Series Page
    Given user is at "author" page with id = "1"
    And user observes "series" card with id = "1"
    When user goes to "series" page with id = "1"
    Then user gets information about "series" with id = "1"
    And user gets "multiple" cards of "book"

  Scenario: Successfully request Book Page
    Given user is at "series" page with id = "1"
    And user observes "book" card with id = "1"
    When user goes to "book" page with id = "1"
    Then user gets information about "book" with id = "1"