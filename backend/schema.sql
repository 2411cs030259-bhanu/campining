-- ============================================================
-- Marketing Analytics Platform - Database Schema
-- Version 1.0
--
-- Run this against MySQL to provision the database:
--   mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS marketing_analytics
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE marketing_analytics;

-- ------------------------------------------------------------
-- users
-- Core authentication table for Version 1.0.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(120) NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                  ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- datasets
-- Tracks each uploaded campaign CSV so future versions can
-- reference historical uploads (Version 2.0+: report storage).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS datasets (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename   VARCHAR(255) NOT NULL,
    row_count     INT NOT NULL DEFAULT 0,
    uploaded_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_datasets_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- reports
-- Generated analytics reports tied to a dataset. Version 1.0
-- creates rows here so Version 2.0 can add retrieval/history
-- without a schema rewrite.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    dataset_id    INT NULL,
    report_filename VARCHAR(255) NOT NULL,
    total_spend   DECIMAL(14,2) DEFAULT 0,
    total_revenue DECIMAL(14,2) DEFAULT 0,
    ctr           DECIMAL(10,4) DEFAULT 0,
    cpc           DECIMAL(10,4) DEFAULT 0,
    cpa           DECIMAL(10,4) DEFAULT 0,
    roas          DECIMAL(10,4) DEFAULT 0,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_reports_dataset
        FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Reserved for future versions (not used in Version 1.0):
--   user_activity   (V3.0 - user history / personal dashboard)
--   organizations   (V9.0 - team & business platform)
--   permissions     (V9.0 - team & business platform)
--   notifications   (future)
-- Creating datasets/reports now with nullable/extendable
-- foreign keys means those tables can be added later by simply
-- adding new FKs, with no breaking changes to this schema.
-- ------------------------------------------------------------
