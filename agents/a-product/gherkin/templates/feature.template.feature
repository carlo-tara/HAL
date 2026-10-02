# language: it
@persona-p01 @job-j01 @need-n01
Feature: Titolo behavior-oriented del Core Job
  # J-01 — statement
  # UI binding: …

  Background:
    Given un investitore nel profilo "P-01"
    And un portafoglio con allocazione sbilanciata rispetto al target

  @journey @happy-path @seed-ss01
  Scenario: Completa il percorso principale fino allo stato di successo
    Given ...
    When ...
    Then ...

  Rule: Input non validi
    @exception @boundary @seed-ss02
    Scenario Outline: Blocca conferma se la condizione non è ammessa
      Given ...
      When ...
      Then ...
      Examples:
        | caso | condizione |
        | vuoto | pesi assenti |
