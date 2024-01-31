/**
 * Copyright (c) Syed Umar Anis.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import {browser} from "$app/environment";

export type SettingName =
  | 'disableBeforeInput'
  | 'measureTypingPerf'
  | 'isRichText'
  | 'isCollab'
  | 'isCharLimit'
  | 'isMaxLength'
  | 'isCharLimitUtf8'
  | 'isAutocomplete'
  | 'showTreeView'
  | 'isEditable'
  | 'showNestedEditorTreeView'
  | 'emptyEditor'
  | 'showTableOfContents'
  | 'tableCellMerge'
  | 'tableCellBackgroundColor';

export type Settings = Record<SettingName, boolean>;

export const isDevPlayground: boolean = false;

export const DEFAULT_SETTINGS: Settings = {
  disableBeforeInput: false,
  emptyEditor: isDevPlayground,
  isAutocomplete: false,
  isCharLimit: false,
  isCharLimitUtf8: false,
  isCollab: false,
  isMaxLength: false,
  isRichText: true,
  measureTypingPerf: false,
  showNestedEditorTreeView: false,
  showTableOfContents: false,
  showTreeView: false,
  tableCellMerge: true,
  tableCellBackgroundColor: true,
  isEditable: true,
};
