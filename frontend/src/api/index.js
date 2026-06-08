export { request, uploadFormData } from './request'

export * from './modules/accessories'
export * from './modules/recommend'
export * from './modules/trips'
export * from './modules/tracking'
export * from './modules/valuations'
export * from './modules/certificates'
export * from './modules/inventory'
export * from './modules/insurance'
export * from './modules/statistics'

import * as accessoriesApi from './modules/accessories'
import * as recommendApi from './modules/recommend'
import * as tripsApi from './modules/trips'
import * as trackingApi from './modules/tracking'
import * as valuationsApi from './modules/valuations'
import * as certificatesApi from './modules/certificates'
import * as inventoryApi from './modules/inventory'
import * as insuranceApi from './modules/insurance'
import * as statisticsApi from './modules/statistics'

export {
  accessoriesApi,
  recommendApi,
  tripsApi,
  trackingApi,
  valuationsApi,
  certificatesApi,
  inventoryApi,
  insuranceApi,
  statisticsApi
}
